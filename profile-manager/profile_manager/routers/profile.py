import asyncio
import datetime
import json
import logging
import os
from threading import Thread
from typing import Dict, List

import requests
from fastapi import APIRouter, Request
from square_auth.auth import Auth


from profile_manager import mongo_client
from profile_manager.core.session_cache import SessionCache
from profile_manager.models import Badge, Submission, Certificate
from profile_manager.settings import ProfileManagerSettings

logger = logging.getLogger(__name__)

settings = ProfileManagerSettings()
router = APIRouter(prefix="/profile")
auth = Auth()
session_cache = SessionCache()


@router.get("/badges", response_model=List[Badge])
async def get_badges(request: Request):
    badges = mongo_client.client.your_database_name.badges_collection.find({})
    return [Badge(**badge) for badge in badges]

@router.get("/submissions", response_model=List[Submission])
async def get_submissions(request: Request):
    submissions = mongo_client.client.your_database_name.submissions_collection.find({})
    return [Submission(**submission) for submission in submissions]

@router.get("/certificates", response_model=List[Certificate])
async def get_certificates(request: Request):
    certificates = mongo_client.client.your_database_name.certificates_collection.find({})
    return [Certificate(**certificate) for certificate in certificates]
