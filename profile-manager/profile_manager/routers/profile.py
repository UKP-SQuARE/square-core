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
    profiles = mongo_client.client.daspChatBotRating.Profile.find({})
    badges = [badge for profile in profiles for badge in profile.get('badges', [])]
    logger.debug(
        "get_badges: {badges}".format(
            badges=", ".join(["{}".format(str(s)) for s in badges])
        )
    )
    badges = [Badge.from_mongo(badge) for badge in badges]
    return badges

@router.get("/submissions", response_model=List[Submission])
async def get_submissions(request: Request):  
    profiles = mongo_client.client.daspChatBotRating.Profile.find({})
    submissions = [submission for profile in profiles for submission in profile.get('submissions', [])]
    logger.debug(
        "get_submissions: {submissions}".format(
            submissions=", ".join(["{}".format(str(s)) for s in submissions])
        )
    )
    submissions = [Submission.from_mongo(submission) for submission in submissions]
    
    return submissions

@router.get("/certificates", response_model=List[Certificate])
async def get_certificates(request: Request):
    profiles = mongo_client.client.daspChatBotRating.Profile.find({})
    certificates = [certificate for profile in profiles for certificate in profile.get('certificates', [])]
    logger.debug(
        "get_certificates: {certificates}".format(
            certificates=", ".join(["{}".format(str(s)) for s in certificates])
        )
    )
    certificates = [Certificate.from_mongo(certificate) for certificate in certificates]
    return certificates
