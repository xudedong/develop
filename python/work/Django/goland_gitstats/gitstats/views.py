#-*- encoding:utf-8 -*-

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth


import logging
import time
import datetime
import subprocess
import os
from models import *
#import access_server

COMMIT_USER_LIST = ["王一","战广月","袁芳芳"]


CUR_YEAR = time.strftime("%Y")
TEMP_FILE = "/Users/DVDFab/goland_gitstats/product.txt"
LOG_FILENAME = "/Users/DVDFab/goland_gitstats/log.txt"
#记录log的函数，参数是log信息
def log(info):
    logging.basicConfig(filename = LOG_FILENAME, level = logging.NOTSET, filemode = 'a', format = '%(asctime)s : %(message)s')
    logging.info(info)

def login(request, template_name = ""):
    if request.session.has_key("username"):
        return HttpResponseRedirect("/display_test_result/")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        passwd = request.POST.get("passwd", "").strip()
        user = auth.authenticate(username=username, password = passwd)
        if user is not None:
            auth.login(request, user)
            request.session["username"] = username
            return HttpResponse("/display_test_result/")
        else:
            return HttpResponse("<a href = ''>密码不正确，点击返回重新登录</a>")
    return render_to_response("login.html")

def format_date_time(src_date):
    from_list_time = src_date.split("-")  
    if len(from_list_time[1]) == 1:
        month = "0" + from_list_time[1]
    else:
        month = from_list_time[1]
    if len(from_list_time[2]) == 1:
        day = "0" + from_list_time[2]
    else:
        day = from_list_time[2]
    format_date = from_list_time[0] + "-" + month + "-" + day
    return format_date

def get_git_log(request):
    product = request.POST.get("product", "").strip()
    fp = open(TEMP_FILE, "w")
    fp.write(product)
    fp.close()
    return HttpResponse(product) 
    result = access_server()
    return render_to_response("get_git_log_success.html")


def show_project(request):
    product = request.POST.get("product", "")
    product_obj = Product.objects.get(name = product)
    project_list = product_obj.project_name.split(";")
    results = ''
    num = 0
    for each_project in sorted(project_list):
        if each_project:
            each_format_project = each_project.split(":")[1].split(".git")[0]
        num += 1
        #if num % 2 == 0:
        record = "<label><input type = 'checkbox' name = 'checkbox' value = '" + each_project + "' checked = 'checked' />" + each_format_project + "</label><br />"
        #else: 
        #    record = "<label><input type = 'checkbox' name = 'checkbox' value = '" + each_project + "' checked = 'checked' />" + each_format_project + "</label>" + "&nbsp;"*10
        results += record
    #results = "</table>"
    return HttpResponse(results, content_type = 'application/json')
    return HttpResponse(simplejson.dumps(results), content_type = 'application/json')

def index(request):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "查询中心"
    context["page_title"] = page_title
    authors = Author.objects.all().order_by("name")
    products = Product.objects.all()
    projects = Project.objects.all()
    context["authors"] = authors
    context["products"] = products
    context["projects"] = projects
    
    author = request.GET.get("author", "").strip()
    product = request.GET.get("product", "").strip()
    project = request.GET.get("project", "").strip()
    start_time = request.GET.get("start_time", "").strip()
    end_time = request.GET.get("end_time", "").strip()
    #如果所有条件为空，则只限定日期
    if not(author or product or start_time or end_time):
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        #默认情况下只显示2天以内的log
        days = 2
        start_time = get_time(days)
        qs = Commit_Record.objects.filter(commit_time__gte = start_time).order_by("-commit_time")
        commit_record = qs.filter(commit_time__lte = end_time)
        if not commit_record:
            commit_record = ""
            empty_message = "Sorry, but there is no result in default %d days!" % days
            context["empty_message"] = empty_message
            
    #只要有一个条件不为空
    else:
        if product:
            checkbox_list = request.GET.getlist("checkbox")
            format_project_list = []
            for each_project in checkbox_list:
                each_format_project = each_project.split(":")[1].split(".git")[0]
                format_project_list.append(each_format_project)
            checkbox_url = ""
            for record in checkbox_list:
                checkbox_url += "checkbox="+record + "&"
            selected_project_list = request.GET.getlist("selected_project")
            #return HttpResponse(selected_project_list)
            url = request.get_full_path()
            if "&page=" in url:
                pass
            else:
                #cmd = "python /Users/DVDFab/goland_gitstats/analyze_log/webpage/run_git_log.py " + ";".join(checkbox_list)
                cmd = "python /Users/DVDFab/goland_gitstats/analyze_log/webpage/run_git_log.py " + product
                subprocess.call(cmd, cwd = "/Users/DVDFab/goland_gitstats/analyze_log/webpage", shell = True)
                #p = subprocess.Popen(cmd, cwd = "/Users/DVDFab/goland_gitstats/analyze_log/webpage",stdout = subprocess.PIPE, shell = True)
                #content = p.stdout.read()
                #fp = open("/Volumes/qqq.txt", "w")
                #fp.write(content)
                #fp.close()
        if start_time:
            start_time = format_date_time(start_time)
        end_time = format_date_time(end_time) if end_time else time.strftime("%Y-%m-%d %H:%M:%S")
            
        try:
            author_obj = Author.objects.get(name = author)
        except Author.DoesNotExist:
            author_obj = ""
            
        try:
            product_obj = Product.objects.get(name = product)
            qs0 = product_obj.commit_record.all().order_by("-commit_time")
            package_nas_path = product_obj.package_nas_path
        except Product.DoesNotExist:
            product_obj = ""
            qs0 = Commit_Record.objects.all().order_by("-commit_time")
            package_nas_path = ""
            
        try:
            project_obj = Project.objects.get(name = project)
        except Project.DoesNotExist:
            project_obj = ""
            
        search_dict = {}
        if author_obj:
            search_dict["author"] = author_obj
        if project_obj:
            search_dict["project"] = project_obj
        qs1 = qs0.filter(**search_dict)

        if start_time:
            if len(start_time) == 10:
                start_time += " 00:00:00"
            qs2 = qs1.filter(commit_time__gte = start_time)
        else:
            qs2 = qs1
                       
        if end_time:
            if len(end_time) == 10:
                end_time += " 23:59:59"
            commit_record = qs2.filter(commit_time__lte = end_time)
        else:
            commit_record = qs2
        #commit_record= qs1
        if not commit_record:
            commit_record = ""
            empty_message = "Sorry, but your search does not contain any result!"
            context["empty_message"] = empty_message
        context["author"] = author
        context["product"] = product
        context["project"] = project
        context["start_time"] = start_time
        context["end_time"] = end_time
        context["package_nas_path"] = package_nas_path
    if product and checkbox_list:   
        context["checkbox_list"] = checkbox_list
        commit_record_list, project_id_list = filter_commit_record(commit_record, checkbox_list) 
        if commit_record:
            commit_record = commit_record.filter(project_id__in = project_id_list)
        #commit_record = commit_record_list
        #context["selected_project_list"] = selected_project_list
        context["format_project_list"] = format_project_list
        context["checkbox_url"] = checkbox_url
    context["all_length"] = len(commit_record)
    if commit_record:
        page, paginator, page_range, commit_record = fenye(request,commit_record)
        sort, new_list_record_order = order_sort(request, commit_record)
        #new_list_record_order = "111"
        context["page"] = page
        context["paginator"] = paginator
        context["page_range"] = page_range
        context["sort"] = sort
        context["commit_record_order"] = new_list_record_order
        #return HttpResponse(new_list_record_order) 
    #无论commit_record是否为空，都需要将值传到模板里面去    
    context["commit_record"] = commit_record
    return render_to_response("index.html", context)


def order_sort(request, commit_record):
    ziduan = request.GET.get("ziduan", "").strip()
    sort = request.GET.get("sort", "").strip()
    new_list_param = []
    new_list_record = []
    new_list_record_order = []
    if ziduan:
        for record in ["id", "author", "project","branch_name","commit_time","commit_version","commit_message"]:
            if ziduan == record:
                for each_record in commit_record:
                    record_value = getattr(each_record, ziduan, "")
                    new_list_record.append((record_value, each_record))
                    new_list_param.append(record_value)
                break
        new_list_param1 = sorted([i for i in set(new_list_param)])
        for i in new_list_param1:
            for j in new_list_record:
                if i in j:
                    new_list_record_order.append(j[1])
        if sort == "2":
            new_list_record_order = new_list_record_order[::-1]
            sort = "1"
        else:
            new_list_record_order = new_list_record_order
            sort = "2"
    else:
        new_list_record_order = commit_record
    return sort,new_list_record_order 
    


def filter_commit_record(commit_record, checkbox_list):
    commit_record_list = []
    project_id_list = []
    for each_record in checkbox_list:
        try:
            project_obj = Project.objects.get(name=each_record)
            project_id = project_obj.id
            project_id_list.append(project_id)
            if commit_record:
                commit_record_list.extend(commit_record.filter(project_id = project_id))
        except Project.DoesNotExist:
            pass
    return commit_record_list, project_id_list

                              
def fenye(request, commit_record):
    #使用分页类显示分页
    after_range_num = 5
    befor_range_num = 4
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    paginator = Paginator(commit_record, 50)

    #跳转至请求页面，如果该页面不存在或者超过则跳转至尾页
    try:
        commit_record = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        page = paginator.num_pages
        commit_record = paginator.page(page)
    if page >= after_range_num:
        page_range = paginator.page_range[page - after_range_num: page + befor_range_num]
    else:
        page_range = paginator.page_range[0: page + befor_range_num]
    return page, paginator, page_range, commit_record


#获得时间
def get_time(days):
    t1 = time.localtime()#current date
    t2=datetime.datetime(t1[0],t1[1],t1[2],t1[3],t1[4],t1[5])   
    t3=t2-datetime.timedelta(days=days)
    t3=str(t3)
    return t3


#显示所有的作者
def display_author(request):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "显示所有作者"
    context["page_title"] = page_title
    authors = Author.objects.all()
    context["authors"] = authors
    return render_to_response("display_author.html", context)


#显示所有的工程
def display_project(request):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "显示所有工程"
    context["page_title"] = page_title
    projects = Project.objects.all()
    context["projects"] = projects
    return render_to_response("display_project.html", context)


#显示所有的产品与工程对应列表
def display_product_project(request):
    product_list = []
    context_all = {}
    context_all["CUR_YEAR"] = CUR_YEAR
    page_title = "显示产品与工程对应列表"
    context_all["page_title"] = page_title
    products = Product.objects.all()
    for each_product in products:
        context = {}
        product_id = each_product.id
        product_name = each_product.name
        product_project_name = each_product.project_name
        product_package_nas_path = each_product.package_nas_path
        product_project_name = " ; ".join([i.split(":")[1].split(".git")[0] for i in product_project_name.split(";") if i.strip()])
        context["product_id"] = product_id
        context["product_name"] = product_name
        context["product_project_name"] = product_project_name
        context["product_package_nas_path"] = product_package_nas_path
        product_list.append(context)
    context_all["product_list"] = product_list
    return render_to_response("display_product_project.html", context_all)


#添加产品与对应的工程
def add_product_project(request):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "添加产品与对应工程"
    context["page_title"] = page_title
    if request.method == "POST":
        product_name = request.POST.get("product_name", "").strip()
        #builder_name = request.POST.get("builder_name", "").strip()
        builder_name = ""
        project_name = request.POST.get("project_name", "").strip()
        package_nas_path = request.POST.get("package_nas_path", "").strip()

        try:
            product_record = Product.objects.get(name=product_name)
            product_id = product_record.id
            context["product_id"] = product_id
            page_title = "已经存在"
            context["page_title"] = page_title
            return render_to_response("exist.html", context)
        except Product.DoesNotExist:
            pass
        #product_record = Product.objects.filter(name=product_name)
        #if product_record:
        #    return render_to_response("exist.html", locals())
        
        #if product_name and builder_name and project_name and package_nas_path:
        if product_name and project_name and package_nas_path:
            if "," in project_name:
                project_name = project_name.replace(",", ";")
             
            product = Product(name = product_name, builder_name = builder_name, \
                              project_name = project_name,package_nas_path = package_nas_path)
            product.save()

            #去除两边的空白符     
            project_name_list = [i.strip() for i in project_name.split(";")]
        
            for each_project in project_name_list:
                if "@" in each_project and ":" in each_project and ".git" in each_project:
                    project = Project.objects.filter(name = each_project)
                    if not project:
                        project = Project(name = each_project)
                        project.save()
            return HttpResponseRedirect('/add_product_project/')
    return render_to_response("add_product_project.html", context)


#修改产品与对应的工程
def update_product_project(request, param):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    context["param"] = param
    page_title = "修改产品与对应工程"
    context["page_title"] = page_title
    try:
        product_record = Product.objects.get(id = param)
        product_name = product_record.name
        builder_name = product_record.builder_name
        project_name = product_record.project_name
        package_nas_path = product_record.package_nas_path
    except Product.DoesNotExist:
        product_name = ""
        builder_name = ""
        project_name = ""
        package_nas_path = ""

    context["product_name"] = product_name
    context["builder_name"] = builder_name
    context["project_name"] = project_name
    context["package_nas_path"] = package_nas_path
        
    if request.method == "POST":
        context["CUR_YEAR"] = CUR_YEAR
        page_title = "修改成功"
        context["page_title"] = page_title
        product_record = Product.objects.filter(id = param)
        product_name = request.POST.get("product_name", "").strip()
        #builder_name = request.POST.get("builder_name", "").strip()
        project_name = request.POST.get("project_name", "").strip()
        package_nas_path = request.POST.get("package_nas_path", "").strip()
        if "," in project_name:
            project_name = project_name.replace(",", ";")
             
        product_record.update(name = product_name, builder_name = builder_name, project_name = project_name, package_nas_path = package_nas_path)
            

        #去除两边的空白符     
        project_name_list = [i.strip() for i in project_name.split(";")]
        
        for each_project in project_name_list:
            if "@" in each_project and ":" in each_project and ".git" in each_project:
                project = Project.objects.filter(name = each_project)
                if not project:
                    project = Project(name = each_project)
                    project.save()
        context["success_url"] = "display_product_project"
        return render_to_response("update_success.html", context)
        
    return render_to_response("update_product_project.html", context)


def test_result_order_sort(request, commit_record):
    ziduan = request.GET.get("ziduan", "").strip()
    sort = request.GET.get("sort", "").strip()
    new_list_param = []
    new_list_record = []
    new_list_record_order = []
    if ziduan:
        for record in ["id", "commit_user", "product","package_name","branch_name","plcore_branch","join_time","verification_result"]:
            if ziduan == record:
                for each_record in commit_record:
                    if ziduan == "verification_result":
                        changelog_obj = each_record[0].test_result_set.all()
                        verify_result = changelog_obj[0].verification_result if changelog_obj else ""
                        new_list_record.append((verify_result, each_record))
                        new_list_param.append(verify_result)
                    else:
                        record_value = getattr(each_record[0], ziduan, "")
                        new_list_record.append((record_value, each_record))
                        new_list_param.append(record_value)
                break
        new_list_param1 = sorted([i for i in set(new_list_param)])
        for i in new_list_param1:
            for j in new_list_record:
                if i in j:
                    new_list_record_order.append(j[1])
        if sort == "2":
            new_list_record_order = new_list_record_order[::-1]
            sort = "1"
        else:
            new_list_record_order = new_list_record_order
            sort = "2"
    else:
        new_list_record_order = commit_record
    return sort,new_list_record_order 


#显示所有测试结果
def display_test_result(request):
    context = {}
    branch_name_list = []
    plcore_branch_list = []
    verification_result_list = ["YES", "NO"]
    context["commit_user_list"] = COMMIT_USER_LIST
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "显示所有测试结果"
    context["page_title"] = page_title
    products = Product.objects.all()
    test_results = Test_Result.objects.all()
    for each_test_result in test_results:
        if each_test_result.branch_name not in branch_name_list:
            branch_name_list.append(each_test_result.branch_name)
        if each_test_result.plcore_branch not in plcore_branch_list:
            plcore_branch_list.append(each_test_result.plcore_branch)
    context["products"] = products
    context["branch_name_list"] = [i for i in set(branch_name_list)]
    context["plcore_branch_list"] = [i for i in set(plcore_branch_list)]
    context["verification_result_list"] = verification_result_list
    
    product = request.GET.get("product", "").strip()
    commit_user = request.GET.get("commit_user", "").strip()
    branch_name = request.GET.get("branch_name", "").strip()
    plcore_branch = request.GET.get("plcore_branch", "").strip()
    verification_result = request.GET.get("verification_result", "").strip()
    start_time = request.GET.get("start_time", "").strip()
    end_time = request.GET.get("end_time", "").strip()
    context["product"] = product
    context["commit_user"] = commit_user
    context["branch_name"] = branch_name
    context["plcore_branch"] = plcore_branch
    context["verification_result"] = verification_result
    if start_time:
        start_time = format_date_time(start_time)
    if end_time:
        end_time = format_date_time(end_time)
    new_test_results = []
    flag = True
    if not(product or branch_name or plcore_branch or verification_result or start_time or end_time):
        for each_record in test_results:
            new_test_results.append((each_record,each_record.test_result_set.all()))
    else:
        qs0 = test_results.filter(product = product) if product else test_results
        qs1 = qs0.filter(commit_user = commit_user) if commit_user else qs0
        qs2 = qs1.filter(branch_name = branch_name) if branch_name else qs1
        qs3 = qs2.filter(plcore_branch = plcore_branch) if plcore_branch else qs2
        if len(start_time) == 10:
            start_time += " 00:00:00"
        qs4 = qs3.filter(join_time__gte = start_time) if start_time else qs3
        if len(end_time) == 10:
            end_time += " 23:59:59"
        qs5 = qs4.filter(join_time__lte = end_time) if end_time else qs4
        if verification_result:
            flag = False
            qs6 = []
            #将每一条记录信息和对应的changelog记录以元组为元素添加到列表中，形成一一对应的关系
            for each_record in qs5:
                if each_record.test_result_set.all().filter(verification_result = verification_result):
                    qs6.append((each_record, each_record.test_result_set.all().filter(verification_result = verification_result)))
        else:
            qs6 = qs5
        if flag:
            temp_list = []
            for each_record in qs6:
                temp_list.append((each_record, each_record.test_result_set.all()))
        new_test_results = temp_list if flag else qs6

    test_results = new_test_results
    page, paginator, page_range, test_results = fenye(request,test_results)
    context["page"] = page
    context["paginator"] = paginator
    context["page_range"] = page_range
    context["test_results"] = test_results
    context["start_time"] = start_time
    context["end_time"] = end_time
    #return HttpResponse(start_time)
    sort, new_list_record_order = test_result_order_sort(request, test_results)
    context["sort"] = sort
    if not new_list_record_order:
        new_list_record_order = ""
        empty_message = "your search do not have any results!"
        context["empty_message"] = empty_message
    context["test_results_order"] = new_list_record_order
    return render_to_response("display_test_result.html", context)

#display details
def display_details(request, param):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    page_title = "显示详细测试结果"
    context["page_title"] = page_title
    test_result = Test_Result.objects.get(id = param)
    #changelog = test_result.changelog_set.all()
    changelog = test_result.test_result_set.all()[::-1]
    context["test_result"] = test_result
    context["changelog"] = changelog
    return render_to_response("display_details.html", context)
  

def get_changelog_values(post_dict):
    flag_str = "changelog"
    temp_list = []
    changelog_list = []
    for each_key in post_dict.keys():
        if flag_str in each_key:
            temp_each_key = each_key.replace(flag_str, "")
            #try:
            temp_list.append(int(temp_each_key))
            #except Exception, e:
            #    temp_list.append(float(temp_each_key))
    for record in sorted(temp_list):
        changelog_list.append(flag_str + str(record))
    return changelog_list
  

#add test result
#@login_required
def add_test_result(request):
    context = {}
    context["CUR_YEAR"] = CUR_YEAR
    context["commit_user_list"] = COMMIT_USER_LIST
    page_title = "添加新的测试结果"
    context["page_title"] = page_title
    products = Product.objects.all()
    context["products"] = products
    if request.method == "POST":
        commit_user = request.POST.get("commit_user", "").strip()
        product = request.POST.get("product", "").strip()
        branch_name = request.POST.get("branch_name", "").strip()
        package_name = request.POST.get("package_name", "").strip()
        package_path = request.POST.get("package_path", "").strip()
        plcore_branch = request.POST.get("plcore_branch", "").strip()
        changelog1 = request.POST.get("changelog1", "").strip()
        verification_result1 = request.POST.get("verification_result1", "").strip()
        remark_explantion1 = request.POST.get("remark_explantion1", "").strip()
        supplement_explantion = request.POST.get("supplement_explantion", "").strip()
        join_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if commit_user and product and package_name:
            test_result = Test_Result(commit_user = commit_user, product = product, branch_name = branch_name, package_name = package_name, package_path = package_path, \
                                      plcore_branch = plcore_branch,join_time = join_time, supplement_explantion = supplement_explantion)
            test_result.save()

            changelog_list = get_changelog_values(request.POST)
            num = 1
            #return HttpResponse(changelog_list)
            for each_key in changelog_list:
                each_num = each_key.replace("changelog", "")
                changelog = Changelog(test_result = test_result, content = request.POST["changelog" + each_num], \
                                      verification_result = request.POST["verification_result" + each_num], remark_explantion = request.POST["remark_explantion" + each_num])
                changelog.save()
                num += 1
            return HttpResponseRedirect("/display_test_result/")
    return render_to_response("add_test_result.html", context)


#修改测试结果
#@login_required
def update_test_result(request, param):
    context = {}
    all_changelog_list = []
    context["CUR_YEAR"] = CUR_YEAR
    context["param"] = param
    page_title = "修改测试结果"
    context["page_title"] = page_title
    test_result = Test_Result.objects.get(id = int(param))
    changelog_list = test_result.test_result_set.all()
    changelog_list_new = changelog_list[::-1]
    commit_user = test_result.commit_user
    product = test_result.product
    branch_name = test_result.branch_name
    package_name = test_result.package_name
    package_path = test_result.package_path
    plcore_branch = test_result.plcore_branch
    for each_record in changelog_list_new:
        context1 = {}
        context1["changelog"] = each_record.content
        context1["verification_result"] = each_record.verification_result
        context1["remark_explantion"] = each_record.remark_explantion
        all_changelog_list.append(context1)
    #changelog = test_result.changelog
    #verification_result = test_result.verification_result
    #remark_explantion = test_result.remark_explantion
    supplement_explantion = test_result.supplement_explantion

    context["commit_user"] = commit_user
    context["product"] = product
    context["branch_name"] = branch_name
    context["package_name"] = package_name
    context["package_path"] = package_path
    context["plcore_branch"] = plcore_branch
    #context["changelog"] = changelog
    #context["verification_result"] = verification_result
    #context["remark_explantion"] = remark_explantion
    context["supplement_explantion"] = supplement_explantion
    context["all_changelog_list"] = all_changelog_list
    
    if request.method == "POST":
        page_title = "修改成功"
        context["page_title"] = page_title
        test_result_obj = Test_Result.objects.filter(id = param)
        commit_user = request.POST.get("commit_user", "").strip()
        product = request.POST.get("product", "").strip()
        branch_name = request.POST.get("branch_name", "").strip()
        package_name = request.POST.get("package_name", "").strip()
        package_path = request.POST.get("package_path", "").strip()
        plcore_branch = request.POST.get("plcore_branch", "").strip()
        changelog = request.POST.get("changelog", "").strip()
        verification_result = request.POST.get("verification_result", "").strip()
        remark_explantion = request.POST.get("remark_explantion", "").strip()
        supplement_explantion = request.POST.get("supplement_explantion", "").strip()
        if commit_user and product and package_name:
            test_result_obj.update(commit_user = commit_user, product = product,branch_name = branch_name, package_name = package_name, package_path = package_path, \
                                   plcore_branch = plcore_branch, supplement_explantion = supplement_explantion)
            changelog_list.delete()
            new_changelog_list = get_changelog_values(request.POST)
            num = 1
            for each_key in new_changelog_list:
                each_num = each_key.replace("changelog", "")
                #return HttpResponse(test_result)
                changelog = Changelog(test_result = test_result, content = request.POST["changelog" + each_num],\
                                      verification_result = request.POST["verification_result" + each_num], remark_explantion = request.POST["remark_explantion" + each_num])
                changelog.save()
                num += 1
            context["success_url"] = "display_test_result"
            return render_to_response("update_success.html", context)
    return render_to_response("update_test_result.html", context)
