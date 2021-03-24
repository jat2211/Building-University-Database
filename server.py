#!/usr/bin/env python

"""
Columbia's COMS W4111.003 Introduction to Databases Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@104.196.152.219/proj1part2
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.152.219/proj1part2"
#
DATABASEURI = "postgresql://jat2211:@J4y123gmail@35.227.37.35/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print( "uh oh, problem connecting to database" )
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def index():
  return render_template("index.html")


@app.route('/homepage')
def homepage():
  return render_template("index.html")


@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/managedata', methods = ['GET','POST'])
def managedata():
    if request.method == "POST":

        print(request.form["table"])
        print(request.form["add"])

        addstring = "INSERT INTO "

        addstring += request.form["table"] + " VALUES(" + request.form["add"] + ")"

        print(addstring)

        cursor = g.conn.execute(addstring)
        cursor.close()
        return render_template("managedata.html",string_="Success!")

    else:

        cursor = g.conn.execute("SELECT major_name FROM Major")
        names = []
        for result in cursor:
          names.append(result['major_name'])  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("managedata.html", **context)


@app.route('/displaymajors', methods = ['GET', 'POST'])
def displaymajors():

    if request.method == "POST" and ( (request.form["majorname"]) or (request.form["majorid"])):

        print(request.form["majorid"])

        print(request.form["majorname"])

        dispmajstring = "SELECT * FROM Major WHERE "

        if(request.form["majorname"] and request.form["majorid"]):
            dispmajstring += "major_name = " + "'" + request.form["majorname"] + "'" + " AND major_id = " + "" + request.form["majorid"] + ""

        elif(request.form["majorname"]):
            dispmajstring += "major_name = " + "'" + request.form["majorname"] + "'"

        elif(request.form["majorid"]):
            dispmajstring += "major_id = " + "'" + request.form["majorid"] + "'"

        else:
            dispmajstring += "major_id = " + "" + request.form["majorid"] + ""

        print(dispmajstring)
        cursor = g.conn.execute(dispmajstring)
        names = []
        for result in cursor:
          columns = list((result[('major_name')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaymajors.html", **context)

    else:

        cursor = g.conn.execute("SELECT * FROM Major")
        names = []
        for result in cursor:
          columns = list((result[('major_name')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaymajors.html", **context)


@app.route('/passedprof1', methods=['GET', 'POST'])
def passedprof1():

    if request.method == "POST":

        cursor = g.conn.execute("SELECT prof_id, prof_name FROM Professor")
        names = []
        for result in cursor:
            columns = list((result[('prof_id')],result[('prof_name')]))
            names.append(columns)
        cursor.close()
        context = dict(data = names)

        bigstr = "SELECT stud_id, stud_name, course_id, course_name FROM Student NATURAL JOIN ( "
        bigstr += "SELECT * FROM ( "
        bigstr += "SELECT stud_id, P.course_id, C.course_name, C.prof_id FROM Passed P "
        bigstr += "INNER JOIN Class C ON P.course_id=C.course_id ) AS abc WHERE prof_id = "
        bigstr += request.form["pazz"]
        bigstr += " ) as qwe"

        cursor2 = g.conn.execute(bigstr)
        names2 = []
        for result in cursor2:
            columns2 = list((result[('stud_id')],result[('stud_name')],result[('course_id')],result[('course_name')]))
            names2.append(columns2)
        cursor2.close()
        context2 = dict(data2 = names2)

        return render_template("passedprof1.html", **context, **context2)

    else:

        cursor = g.conn.execute("SELECT prof_id, prof_name FROM Professor")
        names = []
        for result in cursor:
            columns = list((result[('prof_id')],result[('prof_name')]))
            names.append(columns)
        cursor.close()
        context = dict(data = names)

        return render_template("passedprof1.html", **context)


@app.route('/newstudents', methods=['GET', 'POST'])
def newstudents():

    if request.method == "POST":

        if request.form["status"] == "new":

            querystr = "SELECT S.stud_id, S.stud_name FROM Student S WHERE EXISTS (SELECT I.stud_id FROM Passed I WHERE I.stud_id=S.stud_id)"

            cursor = g.conn.execute(querystr)
            names = []
            for result in cursor:
                columns = list((result[('stud_id')],result[('stud_name')]))
                names.append(columns)
            cursor.close()
            context = dict(data = names)

            return render_template("newstudents.html", **context)

        else:

            querystr = "SELECT S.stud_id, S.stud_name FROM Student S WHERE NOT EXISTS (SELECT I.stud_id FROM Passed I WHERE I.stud_id=S.stud_id)"

            cursor = g.conn.execute(querystr)
            names = []
            for result in cursor:
                columns = list((result[('stud_id')],result[('stud_name')]))
                names.append(columns)
            cursor.close()
            context = dict(data = names)

            return render_template("newstudents.html", **context)

    else:

            return render_template("newstudents.html")


@app.route('/trackprogstep1', methods=['GET', 'POST'])
def trackprogstep1():

    if request.method == "POST":

        #if not request.form["corez"]:
            print("xx")
            print(request.form.get("trackz", None))

            cursor = g.conn.execute("SELECT track_id, track_name FROM Majoring_In NATURAL JOIN Major_Track WHERE stud_id = " + request.form["studid"])
            names = []
            for result in cursor:
                columns = list((result[('track_id')],result[('track_name')]))
                names.append(columns)
            cursor.close()
            context = dict(data = names)
            print("test " + request.form["studid"])


            if request.form.get("trackz", None):

                compq = "SELECT C.course_id, C.course_name FROM Class C "
                compq += "WHERE EXISTS( "
                compq += "SELECT R.course_id FROM Track_Req R "
                compq += "WHERE R.course_id = C.course_id AND R.track_id = "
                compq += request.form["trackz"]
                compq += " ) "
                compq += "AND NOT EXISTS( "
                compq += "SELECT P.course_id FROM Passed P "
                compq += "WHERE P.course_id = C.course_id AND P.stud_id = "
                compq += request.form["studid"]
                compq += " ) "

                print("ccb")
                print(compq)

                cursor2 = g.conn.execute(compq)
                names2 = []
                for result in cursor2:
                    columns2 = list((result[('course_id')],result[('course_name')]))
                    names2.append(columns2)
                cursor2.close()
                context2 = dict(data2 = names2)

                return render_template("trackprog3.html", **context, permstud = request.form["studid"], **context2)

            else:

                return render_template("trackprog2.html", **context, permstud = request.form["studid"])

    else:

        cursor = g.conn.execute("SELECT stud_id FROM Student")
        names = []
        for result in cursor:
          names.append(result['stud_id'])  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)


        return render_template("trackprog1.html", **context)


@app.route('/coreprogstep1', methods=['GET', 'POST'])
def coreprogstep1():

    if request.method == "POST":

        #if not request.form["corez"]:
            print("xx")
            print(request.form.get("corez", None))

            cursor = g.conn.execute("SELECT core_id, core_name FROM Majoring_In NATURAL JOIN Major_Core WHERE stud_id = " + request.form["studid"])
            names = []
            for result in cursor:
                columns = list((result[('core_id')],result[('core_name')]))
                names.append(columns)
            cursor.close()
            context = dict(data = names)
            print("test " + request.form["studid"])


            if request.form.get("corez", None):

                compq = "SELECT C.course_id, C.course_name FROM Class C "
                compq += "WHERE EXISTS( "
                compq += "SELECT R.course_id FROM Core_Req R "
                compq += "WHERE R.course_id = C.course_id AND R.core_id = "
                compq += request.form["corez"]
                compq += " ) "
                compq += "AND NOT EXISTS( "
                compq += "SELECT P.course_id FROM Passed P "
                compq += "WHERE P.course_id = C.course_id AND P.stud_id = "
                compq += request.form["studid"]
                compq += " ) "

                print("ccb")
                print(compq)

                cursor2 = g.conn.execute(compq)
                names2 = []
                for result in cursor2:
                    columns2 = list((result[('course_id')],result[('course_name')]))
                    names2.append(columns2)
                cursor2.close()
                context2 = dict(data2 = names2)

                return render_template("coreprog3.html", **context, permstud = request.form["studid"], **context2)

            else:

                return render_template("coreprog2.html", **context, permstud = request.form["studid"])

        #else:
#
#            cursor1 = g.conn.execute("SELECT core_id, core_name FROM Majoring_In NATURAL JOIN Major_Core WHERE stud_id = 000001")
#            names1 = []
#            for result in cursor1:
#                columns1 = list((result[('core_id')],result[('core_name')]))
#                names1.append(columns1)
#            cursor1.close()
##            context1 = dict(data = names1)
#
#            cursor2 = g.conn.execute("SELECT core_id, core_name FROM Majoring_In NATURAL JOIN Major_Core WHERE stud_id = 000001")
#            name2s = []
#            for result in cursor2:
#                columns2 = list((result[('core_id')],result[('core_name')]))
#                names.append(columns2)
#            cursor2.close()
#            context2 = dict(data2 = names2)



    else:

        cursor = g.conn.execute("SELECT stud_id FROM Student")
        names = []
        for result in cursor:
          names.append(result['stud_id'])  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)


        return render_template("coreprog1.html", **context)





@app.route('/changemajors', methods=['GET', 'POST'])
def changemajors():

    if request.method == "POST":

        #if not request.form["corez"]:

            cursor = g.conn.execute("SELECT major_id, major_name FROM Major ")
            names = []
            for result in cursor:
                columns = list((result[('major_id')],result[('major_name')]))
                names.append(columns)
            cursor.close()
            context = dict(data = names)


            if request.form.get("corez", None):



                theq = "UPDATE Majoring_In SET major_id = " + request.form["corez"] + " WHERE stud_id = " + request.form["studid"]

                cursor2 = g.conn.execute(theq)



                return redirect("/changemajors")

            else:

                return render_template("changemajor2.html", **context, permstud = request.form["studid"])

        #else:
#
#            cursor1 = g.conn.execute("SELECT core_id, core_name FROM Majoring_In NATURAL JOIN Major_Core WHERE stud_id = 000001")
#            names1 = []
#            for result in cursor1:
#                columns1 = list((result[('core_id')],result[('core_name')]))
#                names1.append(columns1)
#            cursor1.close()
##            context1 = dict(data = names1)
#
#            cursor2 = g.conn.execute("SELECT core_id, core_name FROM Majoring_In NATURAL JOIN Major_Core WHERE stud_id = 000001")
#            name2s = []
#            for result in cursor2:
#                columns2 = list((result[('core_id')],result[('core_name')]))
#                names.append(columns2)
#            cursor2.close()
#            context2 = dict(data2 = names2)



    else:

        cursor = g.conn.execute("SELECT stud_id FROM Student")
        names = []
        for result in cursor:
          names.append(result['stud_id'])  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)


        return render_template("changemajor1.html", **context)

#@app.route('/displaymajors')
#def displaymajors():
#
#    cursor = g.conn.execute("SELECT major_name FROM Major")
#    names = []
#    for result in cursor:
#      names.append(result['major_name'])  # can also be accessed using result[0]
#    cursor.close()
#    context = dict(data = names)
#    return render_template("dixsplaymajors.html", **context)




@app.route('/displaystudents', methods = ['GET', 'POST'])
def displaystudents():
    if request.method == "POST" and ( (request.form["studname"]) or (request.form["studid"])):
        print(request.form["studid"])

        print(request.form["studname"])

        dispstudstring = "SELECT * FROM Student WHERE "

        if(request.form["studname"] and request.form["studid"]):
            dispstudstring += "stud_name = " + "'" + request.form["studname"] + "'" + " AND stud_id = " + "" + request.form["studid"] + ""

        elif(request.form["studname"]):
            dispstudstring += "stud_name = " + "'" + request.form["studname"] + "'"

        elif(request.form["studid"]):
            dispstudstring += "stud_id = " + "'" + request.form["studid"] + "'"

        else:
            dispstudstring += "stud_id = " + "" + request.form["studid"] + ""

        print(dispstudstring)
        cursor = g.conn.execute(dispstudstring)
        names = []
        for result in cursor:
          columns = list((result[('stud_name')],result[('stud_id')],result[('tot_creds')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaystudents.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Student")
        names = []
        for result in cursor:
            columns = list((result[('stud_name')],result[('stud_id')],result[('tot_creds')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaystudents.html", **context)


@app.route('/displayprofessors', methods = ['GET', 'POST'])
def displayprofessors():
    if request.method == "POST" and ( (request.form["profname"]) or (request.form["profid"])):
        print(request.form["profid"])

        print(request.form["profname"])

        dispprofstring = "SELECT * FROM Professor WHERE "

        if(request.form["profname"] and request.form["profid"]):
            dispprofstring += "prof_name = " + "'" + request.form["profname"] + "'" + " AND prof_id = " + "" + request.form["profid"] + ""

        elif(request.form["profname"]):
            dispprofstring += "prof_name = " + "'" + request.form["profname"] + "'"

        elif(request.form["profid"]):
            dispprofstring += "prof_id = " + "'" + request.form["profid"] + "'"

        else:
            dispprofstring += "prof_id = " + "" + request.form["profid"] + ""

        print(dispprofstring)
        cursor = g.conn.execute(dispprofstring)
        names = []
        for result in cursor:
          columns = list((result[('prof_name')],result[('prof_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displayprofessors.html", **context)
    else:
      cursor = g.conn.execute("SELECT * FROM Professor")
      names = []
      for result in cursor:
          columns = list((result[('prof_name')],result[('prof_id')]))
          names.append(columns)  # can also be accessed using result[0]
      cursor.close()
      context = dict(data = names)
      return render_template("displayprofessors.html", **context)


@app.route('/displayclasses', methods = ['GET', 'POST'])
def displayclasses():
    if request.method == "POST" and ( (request.form["coursename"]) or (request.form["courseid"])):
        print(request.form["courseid"])

        print(request.form["coursename"])

        dispcoursestring = "SELECT * FROM Class WHERE "

        if(request.form["coursename"] and request.form["courseid"]):
            dispcoursestring += "course_name = " + "'" + request.form["coursename"] + "'" + " AND course_id = " + "" + request.form["courseid"] + ""

        elif(request.form["coursename"]):
            dispcoursestring += "course_name = " + "'" + request.form["coursename"] + "'"

        elif(request.form["courseid"]):
            dispcoursestring += "course_id = " + "'" + request.form["courseid"] + "'"

        else:
            dispcoursestring += "course_id = " + "" + request.form["courseid"] + ""

        print(dispcoursestring)
        cursor = g.conn.execute(dispcoursestring)
        names = []
        for result in cursor:
          columns = list((result[('course_name')],result[('course_id')],result[('creds')],result[('prof_name')],result[('prof_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displayclasses.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Class")
        names = []
        for result in cursor:
            columns = list((result[('course_name')],result[('course_id')],result[('creds')],result[('prof_name')],result[('prof_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displayclasses.html", **context)


@app.route('/majorcores', methods = ['GET', 'POST'])
def majorcores():
    if request.method == "POST" and ( (request.form["corename"]) or (request.form["coreid"])):
        print(request.form["coreid"])

        print(request.form["corename"])

        dispcorestring = "SELECT * FROM Major_Core WHERE "

        if(request.form["corename"] and request.form["coreid"]):
            dispcorestring += "core_name = " + "'" + request.form["corename"] + "'" + " AND core_id = " + "" + request.form["coreid"] + ""

        elif(request.form["corename"]):
            dispcorestring += "core_name = " + "'" + request.form["corename"] + "'"

        elif(request.form["coreid"]):
            dispcorestring += "core_id = " + "'" + request.form["coreid"] + "'"

        else:
            dispcorestring += "core_id = " + "" + request.form["coreid"] + ""

        print(dispcorestring)
        cursor = g.conn.execute(dispcorestring)
        names = []
        for result in cursor:
          columns = list((result[('core_name')],result[('core_id')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("majorcores.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Major_Core")
        names = []
        for result in cursor:
            columns = list((result[('core_name')],result[('core_id')],result[('major_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("majorcores.html", **context)


@app.route('/majortracks', methods = ['GET', 'POST'])
def majortracks():
    if request.method == "POST" and ( (request.form["trackname"]) or (request.form["trackid"])):
        print(request.form["trackid"])

        print(request.form["trackname"])

        disptrackstring = "SELECT * FROM Major_Track WHERE "

        if(request.form["trackname"] and request.form["trackid"]):
            disptrackstring += "track_name = " + "'" + request.form["trackname"] + "'" + " AND track_id = " + "" + request.form["trackid"] + ""

        elif(request.form["trackname"]):
            disptrackstring += "track_name = " + "'" + request.form["trackname"] + "'"

        elif(request.form["trackid"]):
            disptrackstring += "track_id = " + "'" + request.form["trackid"] + "'"

        else:
            disptrackstring += "track_id = " + "" + request.form["trackid"] + ""

        print(disptrackstring)
        cursor = g.conn.execute(disptrackstring)
        names = []
        for result in cursor:
          columns = list((result[('track_name')],result[('track_id')],result[('track_cred')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("majortracks.html", **context)
    else:
        cursor = g.conn.execute("SELECT * FROM Major_Track")
        names = []
        for result in cursor:
            columns = list((result[('track_name')],result[('track_id')],result[('track_cred')],result[('major_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("majortracks.html", **context)


@app.route('/corereqs', methods = ['GET', 'POST'])
def corereqs():
    if request.method == "POST" and ( (request.form["coreid"]) or (request.form["courseid"])):
        print(request.form["coreid"])

        print(request.form["courseid"])

        dispcorereqstring = "SELECT * FROM Core_Req WHERE "

        if(request.form["coreid"] and request.form["courseid"]):
            dispcorereqstring += "core_id = " + "'" + request.form["coreid"] + "'" + " AND course_id = " + "" + request.form["courseid"] + ""

        elif(request.form["courseid"]):
            dispcorereqstring += "course_id = " + "'" + request.form["courseid"] + "'"

        elif(request.form["coreid"]):
            dispcorereqstring += "core_id = " + "'" + request.form["coreid"] + "'"

        else:
            dispcorereqstring += "core_id = " + "" + request.form["coreid"] + ""

        print(dispcorereqstring)
        cursor = g.conn.execute(dispcorereqstring)
        names = []
        for result in cursor:
          columns = list((result[('core_id')],result[('course_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("corereqs.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Core_Req")
        names = []
        for result in cursor:
            columns = list((result[('core_id')],result[('course_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("corereqs.html", **context)


@app.route('/trackreqs', methods = ['GET', 'POST'])
def trackreqs():
    if request.method == "POST" and ( (request.form["trackid"]) or (request.form["courseid"])):
        print(request.form["trackid"])

        print(request.form["courseid"])

        disptrackreqstring = "SELECT * FROM Track_Req WHERE "

        if(request.form["trackid"] and request.form["courseid"]):
            disptrackreqstring += "track_id = " + "'" + request.form["trackid"] + "'" + " AND course_id = " + "" + request.form["courseid"] + ""

        elif(request.form["courseid"]):
            disptrackreqstring += "course_id = " + "'" + request.form["courseid"] + "'"

        elif(request.form["trackid"]):
            disptrackreqstring += "track_id = " + "'" + request.form["trackid"] + "'"

        else:
            disptrackreqstring += "track_id = " + "" + request.form["trackid"] + ""

        print(disptrackreqstring)
        cursor = g.conn.execute(disptrackreqstring)
        names = []
        for result in cursor:
          columns = list((result[('track_id')],result[('course_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("trackreqs.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Track_Req")
        names = []
        for result in cursor:
            columns = list((result[('track_id')],result[('course_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("trackreqs.html", **context)


@app.route('/majoringin', methods = ['GET', 'POST'])
def majoringin():
    if request.method == "POST" and ( (request.form["studid"]) or (request.form["majorid"])):
        print(request.form["studid"])

        print(request.form["majorid"])

        dispmajoringinstring = "SELECT * FROM Majoring_In WHERE "

        if(request.form["studid"] and request.form["majorid"]):
            dispmajoringinstring += "stud_id = " + "'" + request.form["studid"] + "'" + " AND major_id = " + "" + request.form["majorid"] + ""

        elif(request.form["majorid"]):
            dispmajoringinstring += "major_id = " + "'" + request.form["majorid"] + "'"

        elif(request.form["studid"]):
            dispmajoringinstring += "stud_id = " + "'" + request.form["studid"] + "'"

        else:
            dispmajoringinstring += "stud_id = " + "" + request.form["studid"] + ""

        print(dispmajoringinstring)
        cursor = g.conn.execute(dispmajoringinstring)
        names = []
        for result in cursor:
          columns = list((result[('stud_id')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("majoringin.html", **context)

    else:
      cursor = g.conn.execute("SELECT * FROM Majoring_In")
      names = []
      for result in cursor:
          columns = list((result[('stud_id')],result[('major_id')]))
          names.append(columns)  # can also be accessed using result[0]
      cursor.close()
      context = dict(data = names)
      return render_template("majoringin.html", **context)


@app.route('/displaypassed', methods = ['GET', 'POST'])
def displaypassed():
    if request.method == "POST" and ( (request.form["studid"]) or (request.form["courseid"])):
        print(request.form["studid"])

        print(request.form["courseid"])

        disppassedstring = "SELECT * FROM Passed WHERE "

        if(request.form["studid"] and request.form["courseid"]):
            disppassedstring += "stud_id = " + "'" + request.form["studid"] + "'" + " AND course_id = " + "" + request.form["courseid"] + ""

        elif(request.form["courseid"]):
            disppassedstring += "course_id = " + "'" + request.form["courseid"] + "'"

        elif(request.form["studid"]):
            disppassedstring += "stud_id = " + "'" + request.form["studid"] + "'"

        else:
            disppassedstring += "stud_id = " + "" + request.form["studid"] + ""

        print(disppassedstring)
        cursor = g.conn.execute(disppassedstring)
        names = []
        for result in cursor:
          columns = list((result[('stud_id')],result[('course_id')]))
          names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaypassed.html", **context)

    else:
        cursor = g.conn.execute("SELECT * FROM Passed")
        names = []
        for result in cursor:
            columns = list((result[('stud_id')],result[('course_id')]))
            names.append(columns)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = names)
        return render_template("displaypassed.html", **context)


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print( "running on %s:%d" % (HOST, PORT) )
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
