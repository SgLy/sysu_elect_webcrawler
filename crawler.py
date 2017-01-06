# -*- coding: utf-8 -*-
# python verson: 2.7.11


import urllib
import urllib2
import cookielib
from bs4 import BeautifulSoup
from PIL import Image
from StringIO import StringIO

#md5
def md5Upper(str):
    import hashlib
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest().upper()


#PCL short for public course list
class PCL:
    def __init__(self, username, password):
        self.url = 'http://uems.sysu.edu.cn/elect'
        self.loginurl = 'http://uems.sysu.edu.cn/elect/login'
        self.codeurl = 'http://uems.sysu.edu.cn/elect/login/code'
        self.logininfo = {}
        self.logininfo['username'] = username
        self.logininfo['password'] = md5Upper(password)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'}

    def setCookie(self):
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)

    def getCode(self):
        #request for the website
        self.req1 = urllib2.Request(self.url, headers = self.headers)
        try:
            urllib2.urlopen(self.req1)
        except:
            print 'Can\'t open http://uems.sysu.edu.cn/elect.'

        #request for the code
        self.req2 = urllib2.Request(self.codeurl, headers = self.headers)
        try:
            self.codepic = urllib2.urlopen(self.req2)
        except:
            print 'Can\'t get captcha'

        #get the code picture
        img = Image.open(StringIO(self.codepic.read()))
        img.show()

        #ask user to enter the code
        return raw_input('Plaease enter the code of the picture:')

    def login(self):
        try:
            self.setCookie()
        except:
            print 'Can\'t initialization.'

        self.logininfo['j_code'] = self.getCode()

        self.logindata = urllib.urlencode(self.logininfo)
        self.req3 = urllib2.Request(self.loginurl, self.logindata, self.headers)

        try:
            self.respose = urllib2.urlopen(self.req3)
        except:
            print 'Can\'t login in.'

    def pubclass(self):
        #get sid
        self.url = self.respose.geturl()
        self.start = self.url.find('sid=') + 4
        self.sid = self.url[self.start:]

        #set parameters
        self.para = {'kclb': 30, 'xnd':'2015-2016', 'xq': '3','fromSearch': 'false', 'sid': self.sid}
        self.courseurl = 'http://uems.sysu.edu.cn/elect/s/courses?xqm=4&sort=syrs&ord=&xnd=&xq=&' + urllib.urlencode(self.para) + '&conflict=&blank=1&hides=&fromSearch=false&xkjdszid=2016231002001&kcmc=&sjdd=&kkdw=&rkjs=&skyz=&xf1=&xf2=&bkh=&sfbyb='

        #request for the website which shows the list of public corses
        self.req4 = urllib2.Request(self.courseurl, headers = self.headers)
        try:
            self.respose2 = urllib2.urlopen(self.req4)
        except:
            print 'Can\'t get the courses list.'

    def getCourses(self):
        self.pubclass()

        #use BeautifulSoup to get infomation of Courses
        self.soup = BeautifulSoup(self.respose2.read(), 'html.parser')
        #get all a tag
        self.alla = self.soup.find_all('tbody')[1].find_all('a')

        self.courses = []
        #find valid a tag
        for a in self.alla:
            if a.has_attr('href'):
                self.info = {}
                self.info['courseName'] = a.string
                self.info['teacherName'] = a.parent.parent.find_all(attrs = {'class': 'c w'})[0].string

                #find course id
                self.idString = a['onclick']
                self.idStart = self.idString.find('\'') + 1
                self.id = self.idString[self.idStart:-2]
                self.info['id'] = self.id

                self.courses.append(self.info)

    def showCourses(self):

        #show courses list
        self.a = 0
        print '{0:10}'.format('course id'), '{0:50}'.format('course name'), 'teacher name'
        for classes in self.courses:
            #encode('GBK') because in cmd of windows, Chinese characters show well in this form
            print '{0:10}'.format(self.a), '{0:50}'.format(classes['courseName'].encode('GBK')), classes['teacherName']
            self.a = self.a + 1

    def electCourse(self):
        #ask which course you want to elect
        self.courseId = raw_input('Please enter the id of course you want to join:')

        if self.courseId.isdigit():
            self.id = int(self.courseId)
            if self.id < 0 or self.id >= self.a:
                print 'Invalid id!'
            else:
                #request to elect the course
                self.req5 = urllib2.Request('http://uems.sysu.edu.cn/elect/s/elect', urllib.urlencode({'jxbh': self.courses[self.id]['id'], 'sid': self.sid}), self.headers)
                try:
                    self.respose3 = urllib2.urlopen(self.req5)
                    #just print the respose, you can find whether it success
                    print self.respose3.read()
                except:
                    print 'Error while elect the course.'
        else:
            print 'Invalid id!'


username = raw_input('Please enter your username:')
password = raw_input('Please enter your password:')
pcl = PCL(username, password)
pcl.login()
pcl.getCourses()
pcl.showCourses()
pcl.electCourse()
