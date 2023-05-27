from django.shortcuts import render, redirect
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

secrets = settings.API_SECRET_FILE
scopes=['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarInitView(APIView):
    def get(self,request):
        flow = InstalledAppFlow.from_client_secrets_file(secrets,scopes=scopes)
        flow.redirect_uri = 'https://convin-task.codepath.repl.co/rest/v1/calendar/redirect/'
        auth_url, state = flow.authorization_url(access_type='offline',prompt='consent')
        request.session['google_auth_state'] = state
        return redirect(auth_url)

class GoogleCalendarRedirectView(APIView):
    def get(self, request):
        if 'google_auth_state' not in request.session or request.GET.get('state') != request.session['google_auth_state']:
            return Response({'error': 'Invalid state parameter'}, status=status.HTTP_400_BAD_REQUEST)
        flow = InstalledAppFlow.from_client_secrets_file(secrets,scopes=scopes)
        flow.redirect_uri = 'https://convin-task.codepath.repl.co/rest/v1/calendar/redirect/'
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        if not flow.credentials.valid:
            if flow.credentials.expired and flow.credentials.refresh_token:
                flow.credentials.refresh(Request())
        service = build('calendar', 'v3', credentials=flow.credentials)
        events_result = service.events().list(calendarId='primary').execute()
        events = events_result.get('items', [])
        return Response({'events': events},status = status.HTTP_200_OK)