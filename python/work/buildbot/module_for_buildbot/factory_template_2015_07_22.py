#-*- encoding:utf-8 -*-  
#@PydevCodeAnalysisIgnore
from buildbot.process.factory import BuildFactory
from buildbot.steps.source import SVN
from buildbot.steps.shell import ShellCommand
from buildbot.steps.vstudio import VS2008
#import get_data
#import include as CONSTANT
import os.path, time
import MySQLdb

DB_NAME = "auto_create_build"
TB_NAME = "create_build_build_steps"
build_info_id = "var_build_info_id"



class Factory(): 
    def __init__(self, f1_par):
        self.factory = f1_par

    def connect_database(self):
        conn = ""
        cursor = ""
        try:
            conn = MySQLdb.connect(host = 'localhost', user = 'root', passwd = 'sjgldb')   
            conn.select_db(DB_NAME)    
        except Exception, e:
            print str(e)   
        else:
            cursor = conn.cursor()
            select_sql = 'select slave_script_file,work_dir,description from %s where build_info_id = "%s"' % (TB_NAME, build_info_id)
            cursor.execute(select_sql)
            res = cursor.fetchall()
            conn.commit()
            cursor.close()
            conn.close()
        return res
	
    def f_build(self):
        f1 = self.factory

        res = self.connect_database()
        try:
            git_pull = ShellCommand(command="git clone git@10.10.2.31:documents/buildsystem.git " + os.path.basename(os.path.dirname(os.path.dirname(res[0][0]))),
                            workdir = os.path.dirname(os.path.dirname(os.path.dirname(res[0][0]))),
                            haltOnFailure = False,
                            descriptionDone = "update scripts")
            f1.addStep(git_pull)
        except:
            #git_pull = ShellCommand(command="ls -la",
            git_pull = ShellCommand(command="/bin/sh /home/goland/buildbot/scripts/A/script1.sh",
                            workdir = os.path.dirname(os.path.dirname(res[0][0])),
                            haltOnFailure = False,
                            descriptionDone = "update scripts")
            f1.addStep(git_pull)
							
        for each_record in res:
            step = ShellCommand(command="call " + each_record[0],
                                                  workdir = each_record[1],
                                                  haltOnFailure = True,
                                                  descriptionDone = each_record[2])
            f1.addStep(step)

        return f1

		
		
		
		
		
