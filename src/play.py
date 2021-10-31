#python3
from flask import Flask,request,redirect,render_template
import pymysql

#---------------------
#MySQL define
hostname='localhost'
user='root'
password='554646'
database='rugby'
con=pymysql.connect(hostname,user,password,database)
cur=con.cursor()

#---------------------
#global var
userid=None
teamid=None

#---------------------
#flask class define
app=Flask(__name__)
app.debug=True


#---------------------
#Func define
def Mysql_news():
	"""
	execute MySQL command and return lasting three news 
	"""
	cur.execute('select * from clubnews')
	values=[list(i) for i in cur.fetchall()]
	size=len(values)
	values.reverse()
	
	return values[0:3]

def get_news_dict(news_list):
	"""
	return news dict including header reporter date and contents
	"""
	news_dict={}
	size=len(news_list)
	#'NewsDate': datetime.date(2021, 6, 28)
	for i in range(size):
		news_dict[i]={
			'NewsHeader':news_list[i][2],
			'NewsByline':news_list[i][3],
			'NewsDate':str(news_list[i][4]),
			'News':news_list[size-1-i][5],
			}
	
	return news_dict,size

def get_members_info(userid):
	"""
	return login user information
	"""
	cur.execute('select * from members where MemberID='+str(userid))
	values=list(cur.fetchone())
	information={
		'id':values[0],
		'Firstname':values[3],
		'Lastname':values[4],
		'Addr1':values[5],
		'Addr2':values[6],
		'City':values[7],
		'Email':values[8],
		'Phone':values[9],
		'length':8,
		}
	
	return information

def get_members_admin_dict(members_list):
	"""
	reurn the dict of member admin status
	"""
	members_size=len(members_list)
	names={}
	for i in range(members_size):
		name=members_list[i][3]+"-"+members_list[i][4]
		status=members_list[i][12]
		names[name]={'admin':status,'id':members_list[i][0],'teamid':members_list[i][2]}
	
	return names

def Mysql_race():
	"""
	return fixtures
	"""
	cur.execute('select * from fixtures where HomeTeam='+str(teamid))
	homeTeam_race=[list(i) for i in cur.fetchall()]
	cur.execute('select * from fixtures where AwayTeam='+str(teamid))
	awayTeam_race=[list(i) for i in cur.fetchall()]
	
	fixtures={}
	index=0
	for race in homeTeam_race+awayTeam_race:
		home_id=race[2]
		away_id=race[3]
		cur.execute('select TeamName from teams where TeamID='+str(home_id))
		home_name=cur.fetchone()[0]
		cur.execute('select TeamName from teams where TeamID='+str(away_id))
		away_name=cur.fetchone()[0]
		fixtures[index]={
			'id':race[0],
			'date':str(race[1]),
			'HomeTeam':home_id,
			'HomeTeamName':home_name,
			'AwayTeam':away_id,
			'AwayTeamName':away_name,
			'HomeScore':race[4],
			'AwayScore':race[5],
			}
		index+=1
	
	fixtures['length']=len(fixtures)

	return fixtures

def Mysql_grades():
	"""
	return team grades table
	"""
	cur.execute('select * from grades')
	values=[list(i) for i in cur.fetchall()]
	
	return values

def Mysql_teams():
	"""
	execute MySQL command and return members information
	"""
	cur.execute('select * from teams')
	values=[list(i) for i in cur.fetchall()]
	
	return values
	
def Mysql_members():
	"""
	execute MySQL command and return members information
	"""
	cur.execute('select * from members')
	values=[list(i) for i in cur.fetchall()]
	
	return values

def Mysql_clubs():
	"""
	return Mysql clubs table
	"""
	cur.execute('select * from clubs')
	values=[list(i) for i in cur.fetchall()]
	
	return values

def get_clubs(clubs_list):
	"""
	return clubs map
	"""
	clubs_dict={}
	clubs_dict2={}
	index=0
	for club in clubs_list:
		id=club[0]
		name=club[1]
		ground=club[2]
		addr=club[3]
		phone=club[4]
		email=club[5]
		clubs_dict[name]={
			'id':id,
			'name':name,
			'ground':ground,
			'addr':addr,
			'phone':phone,
			'email':email,
		}
		
		clubs_dict2[index]={
			'id':id,
			'name':name,
			'ground':ground,
			'addr':addr,
			'phone':phone,
			'email':email,
		}
		index+=1
	clubs_dict2['length']=len(clubs_dict2)
		
	return clubs_dict,clubs_dict2

def get_id(ids):
	"""
	get id when we inserting data to Mysql table
	"""
	ids.sort()
	id=ids[-1]+1
	while True:
		if id not in ids:
			return id
		id+=1
			
		
def Mysql_join_team(datas,name_map,team_map):
	"""
	Assign a member to a team 
	"""
	name=datas['Name']
	team_name=datas['Team']
	user_id=name_map[name]['id']
	team_id=team_map[team_name]['TeamID']
	
	sql='''\
UPDATE members SET TeamID=%d where MemberID=%d;\
'''%(team_id,user_id)
	cur.execute(sql)
	con.commit()
	
def Mysql_insert_news(datas):
	"""
	Add news items
	"""
	cur.execute('select * from clubnews')
	values=[list(i) for i in cur.fetchall()]
	ids=[]
	for line in values:
		ids.append(line[0])
	id=get_id(ids)
	club_id=23
	sql='''\
INSERT INTO ClubNews VALUES
(%d,%d,'%s','%s','%s','%s');\
'''%(id,club_id,datas['title'],datas['reporter'],datas['date'],datas['text1'])
	cur.execute(sql)
	con.commit()
	
def Mysql_insert_Match(datas,name_map):
	"""
	Add news items
	"""
	
	cur.execute('select * from fixtures')
	values=[list(i) for i in cur.fetchall()]
	ids=[]
	for line in values:
		ids.append(line[0])
	id=get_id(ids)
	date=datas['date']+" "+datas['time']+':00'
	home=datas['Home Team']
	away=datas['Away Team']
	sql='''\
INSERT INTO fixtures VALUES
(%d,'%s',%d,%d,%d,%d);\
'''%(id,date,name_map[home]['TeamID'],name_map[away]['TeamID'],0,0)
	cur.execute(sql)
	con.commit()

def Mysql_admin_update_member(datas,name_map):
	"""
	admin update member details
	"""
	name=datas['membername']
	id=name_map[name]['id']
	firstname=datas['Firstname']
	lastname=datas['Lastname']
	addr1=datas['Addr1']
	addr2=datas['Addr2']
	city=datas['City']
	email=datas['Email']
	phone=int(datas['Phone'])
	birth=datas['BirthDate']
	status=int(datas['MemberShipStatus'])
	access=int(datas['AdminAccess'])
	sql='''\
UPDATE members SET MemberFirstName='%s',MemberLastName='%s',Address1='%s',Address2='%s',\
City='%s',Email='%s',Phone=%d,Birthdate='%s',MembershipStatus=%d,AdminAccess=%d
WHERE MemberID=%d;\
'''%(firstname,lastname,addr1,addr2,city,email,phone,birth,status,access,id)
	cur.execute(sql)
	con.commit()

def Mysql_new_my_team(datas):
	"""
	Add a new team to the club
	"""
	cur.execute('select * from teams')
	values=[list(i) for i in cur.fetchall()]
	ids=[]
	for line in values:
		ids.append(line[0])
	id=get_id(ids)
	
	team_name=datas['TeamName']
	grade=int(datas['grades'])
	
	sql='''\
INSERT INTO teams VALUES
(%d,%d,'%s',%d);\
'''%(id,23,team_name,grade)
	cur.execute(sql)
	con.commit()

def Mysql_new_opp_team(datas,name_map):
	"""
	Add a new (opposition) team to another club 
	"""
	cur.execute('select * from teams')
	values=[list(i) for i in cur.fetchall()]
	ids=[]
	for line in values:
		ids.append(line[0])
	id=get_id(ids)
	
	id2=name_map[datas['clubs']]['id']
	grade=int(datas['grades'])
	name=datas['OppTeamName']
	
	sql='''\
INSERT INTO teams VALUES
(%d,%d,'%s',%d);\
'''%(id,id2,name,grade)
	cur.execute(sql)
	con.commit()

def Mysql_insert_new_member(datas):
	"""
	Add a new member to the club
	"""
	cur.execute('select * from members')
	values=[list(i) for i in cur.fetchall()]
	ids=[]
	for line in values:
		ids.append(line[0])
	id=get_id(ids)
	
	firstname=datas['Firstname']
	lastname=datas['Lastname']
	addr1=datas['Addr1']
	addr2=datas['Addr2']
	city=datas['City']
	email=datas['Email']
	phone=int(datas['Phone'])
	birth=datas['BirthDate']
	status=int(datas['MemberShipStatus'])
	access=int(datas['AdminAccess'])
	
	sql='''\
INSERT INTO members VALUES
(%d,%d,%s,'%s','%s','%s','%s','%s','%s',%d,'%s',%d,%d);\
'''%(id,23,'null',firstname,lastname,addr1,addr2,city,email,phone,birth,status,access)
	
	cur.execute(sql)
	con.commit()
	
def Mysql_members_update(update_data):
	"""
	update member information
	"""
	#[('firstname', ''), ('lastname', ''), ('addr1', ''), 
	#	('addr2', ''), ('city', ''), ('email', ''), ('phone', '')]
	head={
		0:'MemberFirstName',
		1:'MemberLastName',
		2:'Address1',
		3:'Address2',
		4:'City',
		5:'Email',
		6:'Phone',
		}
	datas=list(update_data.values())

	for i in range(len(datas)):
		if datas[i] != '':
			cur.execute('UPDATE members SET '+head[i]+'='+datas[i]+' WHERE MemberID='+str(userid))#UPDATE runoob_tbl SET runoob_title='学习 C++' WHERE runoob_id=3;


def get_teams_grade(grade_list):
	"""
	return teams grades information
	"""
	grade_dict={}
	for grade in grade_list:
		id=grade[0]
		name=grade[1]
		minage=grade[2]
		maxage=grade[3]
		grade_dict[id]={
			'id':id,
			'GradeName':name,
			'MinAge':minage,
			'MaxAge':maxage,
		}
	
	return grade_dict
	

def get_teams_map(teams_list):
	"""
	return my team and other team infomation
	"""
	team_map={}
	myteam=[]
	otherteam=[]
	for team in teams_list:
		teamid=team[0]
		clubid=team[1]
		teamname=team[2]
		teamgrade=team[3]
		team_map[teamname]={
			'TeamID':teamid,
			'ClubID':clubid,
			'TeamName':teamname,
			'TeamGrade':teamgrade,
			}
		if clubid == 23:
			myteam.append(teamname)
		else:
			otherteam.append(teamname)
			
	return team_map, myteam, otherteam
	
def get_old_member(members_list):
	"""
	return old member information
	"""
	old_member={}
	name_to_info={}
	index=0
	for member in members_list:
		id=member[0]
		firstname=member[3]
		lastname=member[4]
		addr1=member[5]
		addr2=member[6]
		city=member[7]
		email=member[8]
		phone=member[9]
		birthday=member[10]
		status=member[11]
		access=member[12]
		
		name_to_info[firstname+'-'+lastname]={
			'id':id,
			'Firstname':firstname,
			'Lastname':lastname,
			'Addr1':addr1,
			'Addr2':addr2,
			'City':city,
			'Email':email,
			'Phone':phone,
			'BirthDate':str(birthday),
			'MemberShipStatus':status,
			'AdminAccess':access,
			}
		
		old_member[index]={
			'id':id,
			'Firstname':firstname,
			'Lastname':lastname,
			'Addr1':addr1,
			'Addr2':addr2,
			'City':city,
			'Email':email,
			'Phone':phone,
			'BirthDate':str(birthday),
			'MemberShipStatus':status,
			'AdminAccess':access,
			}
		index+=1
	old_member['length']=len(old_member)
	return old_member, name_to_info
	

#------------------------
#flast route define
@app.route('/')
def main():
	"""
	first page: /login.html
	"""
	members_list=Mysql_members()
	members_names=get_members_admin_dict(members_list).keys()
	return render_template('login.html',members=members_names)

@app.route('/user',methods=["POST","GET"])
def login():
	"""
	login page: /main.html
	"""
	global userid,teamid
	
	#get loging user name
	user=request.form["name"]
	
	#get user status
	members_list=Mysql_members()
	members_admin_status=get_members_admin_dict(members_list)
	
	#assign two global var userid and teamid
	userid=members_admin_status[user]['id']
	teamid=members_admin_status[user]['teamid']
	
	#get contact information about login user
	user_info=get_members_info(userid)
	
	#get race date and basical information
	fixtures=Mysql_race()
	
	#get news
	news=Mysql_news()
	news_dict,news_size=get_news_dict(news)
	
	#judge user status:
	#admin?
	#common?
	if members_admin_status[user]['admin']==0:
		return render_template('main.html',fixtures=fixtures,news=news_dict,news_size=news_size,user_info=user_info)#json.dumps({"a":1,"b":2})
	
	elif members_admin_status[user]['admin']==1:
		return redirect("/admin")




@app.route('/admin',methods=['GET','POST'])
def admin():
	
	#member list
	members_list=Mysql_members()
	old_member,name_map=get_old_member(members_list)
	
	#team list
	teams=Mysql_teams()
	team_map,my_team,other_team=get_teams_map(teams)
	
	#grade list
	grades=Mysql_grades()
	grades_list=get_teams_grade(grades)
	
	#clubs
	clubs=Mysql_clubs()
	clubs_map,clubs_index=get_clubs(clubs)
	
	#record
	if len(request.form)!=0:
		if request.form['identity']!='None':
			
			#news change
			if request.form['identity']=='News':
				Mysql_insert_news(request.form)
			
			#New_Members
			elif request.form['identity']=='New_Members':
				Mysql_insert_new_member(request.form)
				
			#Old_Member
			elif request.form['identity']=='Old_Member':
				Mysql_admin_update_member(request.form,name_map)
				
			#New_My_Team
			elif request.form['identity']=='New_My_Team':
				Mysql_new_my_team(request.form)
				
			#New_opposition_Team
			elif request.form['identity']=='New_opposition_Team':
				Mysql_new_opp_team(request.form,clubs_map)
				
			#Home_Match
			elif request.form['identity']=='Home_Match':
				Mysql_insert_Match(request.form,team_map)
				
			#Away_Match
			elif request.form['identity']=='Away_Match':
				Mysql_insert_Match(request.form,team_map)
				
			#Practice
			elif request.form['identity']=='Practice':
				Mysql_insert_Match(request.form,team_map)
				
			#Join_Team
			elif request.form['identity']=='Join_Team':
				Mysql_join_team(request.form,name_map,team_map)
			
	#print("************",request.form)
	return render_template('admin.html',clubs_map=clubs_map,clubs_index=clubs_index,grades_list=grades_list,team_map=team_map,my_team=my_team,other_team=other_team,old_member=old_member,name_map=name_map)
	
if __name__=='__main__':
	app.run(host='0.0.0.0',port=9000)
	
