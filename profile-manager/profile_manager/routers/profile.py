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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles")
auth = Auth()
session_cache = SessionCache()


@router.get("/badges", response_model=List[Badge])
async def get_badges(request: Request):
    test = mongo_client.client.daspChatBotRating.Profile
    badges = mongo_client.client.daspChatBotRating.Profile.badges.find({})
    return [Badge(**badge) for badge in badges]

@router.get("/submissions", response_model=List[Submission])
async def get_submissions(request: Request):
    submissions = mongo_client.client.daspChatBotRating.Profile.submissions.find({})
    return [Submission(**submission) for submission in submissions]

@router.get("/certificates", response_model=List[Certificate])
async def get_certificates(request: Request):
    certificates = mongo_client.client.daspChatBotRating.Profile.certificates.find({})
    return [Certificate(**certificate) for certificate in certificates]
