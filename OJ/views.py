from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from OJ.models import *
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from USERS.models import User, Submissions
from OJ.models import Problem, Testcase
from OJ.forms import CodeForm
from datetime import datetime
from time import time

import os
import signal
import subprocess
import os.path
import docker

# Create your views here.
def dashboard(request):
    problems= Problem.objects.all()
    return render(request, 'dashboard.html', {'problems':problems})
    # return HttpResponse("Home dashboard")


def prob_description(request, problem_id):
    #  return HttpResponse("Home dashboard")
    problem = get_object_or_404(Problem, id=problem_id)

    return render(request, 'prob_description.html', {'problem':problem})

login_required(login_url='login')
def verdict(request, problem_id):
    if request.method == 'POST':
        # setting docker-client
        docker_client = docker.from_env()
        Running = "running"

        problem = Problem.objects.get(id=problem_id)
        testcase = Testcase.objects.get(problem_id=problem_id)
        #replacing \r\n by \n in original output to compare it with the usercode output
        testcase.output = testcase.output.replace('\r\n','\n').strip() 

        # score of a problem
        if problem.difficulty=="Easy":
            score = 10
        elif problem.difficulty=="Medium":
            score = 30
        else:
            score = 50


        #setting verdict to wrong by default
        verdict = "Wrong Answer" 
        res = ""
        run_time = 0

        # extract data from form
        form = CodeForm(request.POST)
        user_code = ''
        if form.is_valid():
            user_code = form.cleaned_data.get('user_code')
            user_code = user_code.replace('\r\n','\n').strip()
            
        language = request.POST['language']
        submission = Submissions(user=request.user, problem=problem, submission_time=datetime.now(), 
                                    language=language, user_code=user_code)
        submission.save()

        filename = str(submission.id)

        # if user code is in C++
        if language == "C++":
            extension = ".cpp"
            cont_name = "oj-cpp"
            compile = f"g++ -o {filename} {filename}.cpp"
            clean = f"{filename} {filename}.cpp"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"
            
        elif language == "C":
            extension = ".c"
            cont_name = "oj-c"
            compile = f"gcc -o {filename} {filename}.c"
            clean = f"{filename} {filename}.c"
            docker_img = "gcc:11.2.0"
            exe = f"./{filename}"

        elif language == "Python3":
            extension = ".py"
            cont_name = "oj-py3"
            compile = "python3"
            clean = f"{filename}.py"
            docker_img = "python3"
            exe = f"python {filename}.py"
        
        elif language == "Python2":
            extension = ".py"
            cont_name = "oj-py2"
            compile = "python2"
            clean = f"{filename}.py"
            docker_img = "python2"
            exe = f"python {filename}.py"

        elif language == "Java":
            filename = "Main"
            extension = ".java"
            cont_name = "oj-java"
            compile = f"javac {filename}.java"
            clean = f"{filename}.java {filename}.class"
            docker_img = "openjdk"
            exe = f"java {filename}"


        file = filename + extension
        filepath = settings.FILES_DIR + "/" + file
        code = open(filepath,"w")
        code.write(user_code)
        code.close()

        # checking if the docker container is running or not
        try:
            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)


        # copy/paste the .cpp file in docker container 
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)

        # compiling the code
        cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        if cmp.returncode != 0:
            verdict = "Compilation Error"
            subprocess.run(f"docker exec {cont_name} rm {file}",shell=True)

        else:
            # running the code on given input and taking the output in a variable in bytes
            start = time()
            try:
                res = subprocess.run(f"docker exec {cont_name} sh -c 'echo \"{testcase.input}\" | {exe}'",
                                                capture_output=True, timeout=problem.time_limit, shell=True)
                run_time = time()-start
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
            except subprocess.TimeoutExpired:
                run_time = time()-start
                verdict = "Time Limit Exceeded"
                subprocess.run(f"docker container kill {cont_name}", shell=True)
                subprocess.run(f"docker start {cont_name}",shell=True)
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)


            if verdict != "Time Limit Exceeded" and res.returncode != 0:
                verdict = "Runtime Error"
                

        user_stderr = ""
        user_stdout = ""
        if verdict == "Compilation Error":
            user_stderr = cmp.stderr.decode('utf-8')
        
        elif verdict == "Wrong Answer":
            user_stdout = res.stdout.decode('utf-8')
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
            testcase.output += '\n' 
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"


        # creating Solution class objects and showing it on leaderboard
        user = User.objects.get(username=request.user)
        previous_verdict = Submissions.objects.filter(user=user.id, problem=problem, verdict="Accepted")
        if len(previous_verdict)==0 and verdict=="Accepted":
            user.total_score += score
            user.total_solve_count += 1
            if problem.difficulty == "Easy":
                user.easy_solve_count += 1
            elif problem.difficulty == "Medium":
                user.medium_solve_count += 1
            else:
                user.tough_solve_count += 1
            user.save()

        submission.verdict = verdict
        submission.user_stdout = user_stdout
        submission.user_stderr = user_stderr
        submission.run_time = run_time
        submission.save()
        os.remove(filepath)
        context={'verdict':verdict}
        return render(request,'verdict.html',context)


# def submit_code(request):
#     if request.method == 'POST':
#         form = CodeForm(request.POST)
#         if form.is_valid():
#             # Save submission to database
#             submission = form.save()
#             return redirect('success_url')
#     else:
#         form = CodeForm()
#     return render(request, 'submit_code_template.html', {'form': form})

def contact(request):
    return render (request, 'contact.html')