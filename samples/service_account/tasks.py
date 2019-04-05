#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple command-line sample that demonstrates service accounts.

Lists all the Google Task Lists associated with the given service account.
Service accounts are created in the Google API Console. See the documentation
for more information:

   https://developers.google.com/console/help/#WhatIsKey

Usage:
  $ python tasks.py
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'
import sys

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

# Paste your project ID here.
cloud_project_id = 'modementerpriseemm'
enterprise_name = 'enterprises/LC03btxjav'
policy1 = enterprise_name + '/policies/policy1'
policy2 = enterprise_name + '/policies/policy2'

CALLBACK_URL = 'https://storage.googleapis.com/android-management-quick-start/enterprise_signup_callback.html'

def main(argv):
    # Load the json format key that you downloaded from the Google API
    # Console when you created your service account. For p12 keys, use the
    # from_p12_keyfile method of ServiceAccountCredentials and specify the
    # service account email address, p12 keyfile, and scopes.

    # createEnterprise()
    # createOrUpdatePolicy(policy1)
    # createEnrollmentToken()
    # createWebToken()
    # listDevices()
    # listPolicies()
    deleteDevice()

def getManager():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'key.json',
        scopes='https://www.googleapis.com/auth/androidmanagement')
    androidmanagement = build('androidmanagement', 'v1', credentials=credentials)
    return androidmanagement

def createEnterprise():
    androidmanagement = getManager()
    # Generate a signup URL where the enterprise admin can signup with a Gmail
    # account.
    signup_url = androidmanagement.signupUrls().create(
        projectId=cloud_project_id,
        callbackUrl=CALLBACK_URL
    ).execute()

    print('Please visit this URL to create an enterprise:', signup_url['url'])

    enterprise_token = input('Enter the code: ')

    # Complete the creation of the enterprise and retrieve the enterprise name.
    enterprise = androidmanagement.enterprises().create(
        projectId=cloud_project_id,
        signupUrlName=signup_url['name'],
        enterpriseToken=enterprise_token,
        body={}
    ).execute()

    enterprise_name = enterprise['name']

    print('\nYour enterprise name is', enterprise_name)


def createOrUpdatePolicy(policy_name):
    import json
    androidmanagement = getManager()
    policy_json = '''
        {
        "applications": [
        
          {
            "packageName": "com.ascentnet.modem",
            "installType": "FORCE_INSTALLED",
            "lockTaskAllowed": true,
            "defaultPermissionPolicy": "GRANT"
          }, 
          {
            "packageName": "jp.drjoy.app",
            "installType": "FORCE_INSTALLED",
            "lockTaskAllowed": true,
            "defaultPermissionPolicy": "GRANT"
          }
          , 
          {
            "packageName": "com.hecorat.screenrecorder.free",
            "installType": "FORCE_INSTALLED",
            "lockTaskAllowed": true,
            "defaultPermissionPolicy": "GRANT"
          }
        ],
        "persistentPreferredActivities": [
            {
              "receiverActivity": "jp.drjoy.app/.jp.drjoy.app.presentasion.activity.SplashActivity",
              "actions": [
                "android.intent.action.MAIN"
              ],
              "categories": [
                "android.intent.category.HOME",
                "android.intent.category.LAUNCHER",
                "android.intent.category.DEFAULT"
              ]
            }
          ],
          "kioskCustomLauncherEnabled": true,
          "statusBarDisabled": true,
          "keyguardDisabled": true
        }
        '''

    androidmanagement.enterprises().policies().patch(
        name=policy_name,
        body=json.loads(policy_json)
    ).execute()


def createWebToken():
    androidmanagement = getManager()
    body = {
      "name": "test",
      "value": "test",
      "permissions": [],
      "parentFrameUrl": "https://storage.googleapis.com"
    }
    webToken = androidmanagement.enterprises().webTokens().create(
        parent=enterprise_name,
        body=body
    ).execute()
    print('\nToken value: ', webToken['value'])


def listDevices():
    androidmanagement = getManager()
    device_list = androidmanagement.enterprises().devices().list(
        parent=enterprise_name,
        pageSize=1,
        pageToken="",
    ).execute()
    print('\nToken value: ', device_list)


def listPolicies():
    androidmanagement = getManager()
    device_list = androidmanagement.enterprises().policies().list(
        parent=enterprise_name,
        pageSize=1,
        pageToken="",
    ).execute()
    print('\nToken value: ', device_list)

def createEnrollmentToken():
    androidmanagement = getManager()
    policyName = enterprise_name + '/policies/policy1'
    user_id = 2
    body = {
      "name": "my device %s" %user_id,
      "value": "test %s" %user_id,
      "duration": "604800s",# 60*60*24*7 seconds
      "expirationTimestamp": "2020-10-02T15:01:23.045123456Z",
      "policyName": policyName,
      "qrCode": "test",
      "oneTimeOnly": "false",
      "user": {
          "accountIdentifier": "user%s" %user_id
        }
    }

    enrollToken = androidmanagement.enterprises().enrollmentTokens().create(
        parent=enterprise_name,
        body=body
    ).execute()

    print('\nToken value: ', enrollToken['value'])


def deleteDevice():
    androidmanagement = getManager()
    device_name = 'enterprises/LC03btxjav/devices/3b302764972602c5'
    androidmanagement.enterprises().devices().delete(
        name=device_name,
    ).execute()

if __name__ == '__main__':
  main(sys.argv)
