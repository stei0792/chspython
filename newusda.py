# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 09:05:55 2016

@author: msteinme
"""

import pprint
import pyusda
from tabulate import tabulate

subject = '1'  # subject eg. corn or soybean. codes avalable in document 
strState = '19'  #areacode. codes available in document
strYear = '1996' #year for which the data is being fetched
api_key= 'gYhafzqiKiCmL8lJAksN5qfaCvLYnG9600BgNmgS&report=11&series1=farm&fipsStateCode='+strState+'&year='+strYear
subject = int(subject)
url = 'http://api.data.gov/USDA/ERS/data/Arms/Crop'


ap = pyusda.APIObject(url,api_key)
#pprint.pprint(ap.url)

num=0
n1=0
for n in ap.data['dataTable']:
    n1+=1
print (n1)

strSubj = []
strReport = []
strStatePrint = []
strYear = []
strTopic = []
strEstimate = []
strRse = []
bPLACRES=0
bNITAC = 0
bPHOAC = 0
bPOTAC = 0
bNITLB = 0
bPHOLB = 0
bPOTLB = 0
for n in range(0,n1,1):       
        subj = ap.data['dataTable'][n]['subject_num']
        if subj == subject:
            #print 'Subject:'
            topReq = str(ap.data['dataTable'][n]['topic_abb'])
            if (topReq == "PLACRES" and bPLACRES == 1) or (topReq == "NITLB" and bNITLB == 1) or (topReq == "PHOLB" and bPHOLB == 1) or (topReq == "POTLB" and bPOTLB == 1) or (topReq == "NITAC" and bNITAC == 1) or (topReq == "PHOAC" and bPHOAC == 1) or (topReq == "POTAC" and bPOTAC == 1):
                continue
            else:
                
                if topReq == "F219A1" or topReq == "LIME" or topReq == "CHEMMAN" or topReq == "NINHBTR" or topReq == "NITTST" or topReq == "SOILTST" or topReq == "PLTTSUT" or topReq == "COMPOST":
                    continue
                elif topReq == "PLACRES":
                    bPLACRES = 1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "NITLB":
                    bNITLB = 1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "PHOLB":
                    bPHOLB = 1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "POTLB":
                    bPOTLB = 1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "NITAC":
                    bNITAC =1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "PHOAC":
                    bPHOAC =1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))
                elif topReq == "POTAC":
                    bPOTAC =1
                    
                    strSubj.append(str(ap.data['dataTable'][n]['subject_num']))
                    strReport.append(str(ap.data['dataTable'][n]['report_num']))
                    strStatePrint.append(str(ap.data['dataTable'][n]['state'])) 
                    strYear.append(str(ap.data['dataTable'][n]['stat_year']))
                    strTopic.append(str(ap.data['dataTable'][n]['topic_header']))
                    strEstimate.append(str(ap.data['dataTable'][n]['estimate']))
                    strRse.append(str(ap.data['dataTable'][n]['rse']))



        else:
            num+=1
            continue

#szList = len(strSubj)
#for i in range(0,szList):
tableHeaders = ["Subject","Report","State","Year","Topic","Estimate","Rse"]
table = [
                 [strSubj[0],strReport[0],strStatePrint[0],strYear[0],strTopic[0],strEstimate[0],strRse[0]],
                 [strSubj[1],strReport[1],strStatePrint[1],strYear[1],strTopic[1],strEstimate[1],strRse[1]],
                 [strSubj[2],strReport[2],strStatePrint[2],strYear[2],strTopic[2],strEstimate[2],strRse[2]],
                 [strSubj[3],strReport[3],strStatePrint[3],strYear[3],strTopic[3],strEstimate[3],strRse[3]],
                 [strSubj[4],strReport[4],strStatePrint[4],strYear[4],strTopic[4],strEstimate[4],strRse[4]],
                 [strSubj[5],strReport[5],strStatePrint[5],strYear[5],strTopic[5],strEstimate[5],strRse[5]],
                 [strSubj[6],strReport[6],strStatePrint[6],strYear[6],strTopic[6],strEstimate[6],strRse[6]]
        ]
print (tabulate(table, tableHeaders, tablefmt="simple"))