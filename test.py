import requests
import re
from time import sleep

session = requests.Session()
img = re.compile('<img class="img_verifycode change-code change_verifycode" src="(.*?)" alt="验证码"')
login_url = 'https://zjy2.icve.com.cn/portal/login.html'
login_api = 'https://zjy2.icve.com.cn/common/login/login'
class_list_url = 'https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList'
process_list_url = 'https://zjy2.icve.com.cn/api/study/process/getProcessList'
topic_list_url = 'https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId'
topic_cell_list_url = 'https://zjy2.icve.com.cn/api/study/process/getCellByTopicId'
view_directory_url = 'https://zjy2.icve.com.cn/api/common/Directory/viewDirectory'
cell_log_url = 'https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog'

def login():
    username = input('输入账号：')
    passwd = input('输入密码：')
    img_url = img.findall(session.get(login_url).content.decode())[0]
    with open('img.png', 'wb') as f:
        f.write(session.get(img_url).content)
    result = input('输入验证码：')
    post_data = {'userName': username, 'userPwd': passwd, 'verifyCode': result}
    name = session.post(login_api, data=post_data).json()['displayName']
    print ('*'*50)
    print (name+',登录成功')

def get_class_list():
    return session.post(class_list_url).json()['courseList']

def get_process_list(courseOpenId, openClassId):
    data = {'courseOpenId': courseOpenId, 'openClassId': openClassId}
    return session.post(process_list_url, data=data).json()['progress']

def get_topic_list(courseOpenId, moduleId):
    data = {'courseOpenId': courseOpenId, 'moduleId': moduleId}
    return session.post(topic_list_url, data=data).json()['topicList']

def get_topic_cell_list(courseOpenId, openClassId, topicId):
    data = {'courseOpenId': courseOpenId, 'openClassId': openClassId, 'topicId': topicId}
    return session.post(topic_cell_list_url, data=data).json()['cellList']

def get_view_directory(courseOpenId, openClassId, cellId, moduleId):
    view_data = {
        "courseOpenId": courseOpenId,
        "openClassId": openClassId,
        "cellId": cellId,
        "flag":"s",
        "moduleId": moduleId}
    return session.post(view_directory_url, data=view_data).json()

def post_cell_log(courseOpenId, openClassId, cellId, cellLogId, picNum, studyNewlyTime, token):
    data = {"courseOpenId":courseOpenId,
            "openClassId":openClassId,
            "cellId":cellId,
            "cellLogId":cellLogId,
            "picNum":picNum,
            "studyNewlyTime":studyNewlyTime,
            "studyNewlyPicNum":picNum,
            "token":token}
    return session.post(cell_log_url, data=data).json()




login()

print ('*'*50)
tm = input('选择刷课速度（单位秒，默认10）')
y = 10 if tm=='' else int(tm)
print (str(y)+'s/节')
print ('*'*50)
print ('选择课程（输入序号）')

n = 0
for x in get_class_list():
    print (n, x['courseName'])
    n += 1
    
i = get_class_list()[int(input())]
print ('*'*50)
print ('\n'+i['courseName'])
courseOpenId = i['courseOpenId']  #获取courseOpenId
openClassId = i['openClassId']  #获取openClassId
process_list = get_process_list(courseOpenId, openClassId)
moduleId = process_list['moduleId']  #获取moduleId

for process in process_list['moduleList']:
    print ('    ' + process['name'] + ' -' + str(process['percent']))
    if process['percent'] == 100:
        continue
    percent_id = process['id']  #获取percent_id

    for topic in get_topic_list(courseOpenId, percent_id):
        print ('        ' + topic['name'])
        topic_id = topic['id']

        for cell in get_topic_cell_list(courseOpenId, openClassId, topic_id):
            if cell['stuCellPercent'] == 100:
                print ('            ' + cell['cellName'] + ' -' + str(cell['stuCellPercent']) + '%  以完成')
                continue
            elif cell['categoryName'] == '子节点':
                for i in cell['childNodeList']:
                    print ('            ' + i['cellName'] + ' -' + str(i['stuCellFourPercent']) + '%', end=' ')
                    if i['stuCellFourPercent'] == 100:
                        print ('已完成')
                        continue
                    cell_id = i['Id']
                    view = get_view_directory(courseOpenId, openClassId, cell_id, moduleId)
                    # print (view)
                    picNum = view['pageCount']
                    studyNewlyTime = view['audioVideoLong']
                    guIdToken = view['guIdToken']
                    cellLogId = view['cellLogId']
                    print (post_cell_log(courseOpenId, openClassId, cell_id, cellLogId, picNum, studyNewlyTime, guIdToken)['msg'])
                    sleep(10)
            else:
                print ('            ' + cell['cellName'] + ' -' + str(cell['stuCellPercent']) + '%', end=' ')
                cell_id = cell['Id']
                view = get_view_directory(courseOpenId, openClassId, cell_id, moduleId)
                picNum = view['pageCount']
                studyNewlyTime = view['audioVideoLong']
                guIdToken = view['guIdToken']
                cellLogId = view['cellLogId']
                print (post_cell_log(courseOpenId, openClassId, cell_id, cellLogId, picNum, studyNewlyTime, guIdToken)['msg'])
                sleep(y)