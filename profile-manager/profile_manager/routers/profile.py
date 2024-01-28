import asyncio
import datetime
import json
import logging
import os
from threading import Thread
from typing import Dict, List

import requests
from fastapi import APIRouter, Request, HTTPException
from square_auth.auth import Auth
from bson.objectid import ObjectId

from profile_manager import mongo_client
from profile_manager.core.session_cache import SessionCache
from profile_manager.models import LLM, Badge, Review, Certificate, Profile, LeaderboardEntry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profiles")
auth = Auth()
session_cache = SessionCache()

@router.get("/submissions/{email}", response_model=List[Review])
async def get_submissions(request: Request, email: str = None):
    profile = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    if profile:
        submission_ids = [ObjectId(submission) for submission in profile["Reviews"]]
        submissions = list(mongo_client.client.daspChatBotRating.Review.find({"_id": {"$in": submission_ids}}))
        logger.debug(
            "get_submissions: {submissions}".format(
                submissions=", ".join(["{}".format(str(s)) for s in submissions])
            )
        )
        # Dereferencing Ratings for each submission and its messages
        for submission in submissions:
            llm_id = submission['LLM']
            submission['LLM'] = mongo_client.client.daspChatBotRating.LLM.find_one({"_id": llm_id})
            if 'Rating' in submission and isinstance(submission['Rating'], ObjectId):
                rating_id = submission['Rating']
                submission['Rating'] = mongo_client.client.daspChatBotRating.Rating.find_one({"_id": rating_id})
            for message in submission.get('Messages', []):
                if 'Rating' in message and message['Rating'] and isinstance(message['Rating'], ObjectId):
                    rating_id = message['Rating']
                    message['Rating'] = mongo_client.client.daspChatBotRating.Rating.find_one({"_id": rating_id})
        logger.debug(
            "get_submissions: {submissions}".format(
                submissions=", ".join(["{}".format(str(s)) for s in submissions])
            )
        )
        submissions = [Review.from_mongo(submission) for submission in submissions]
        return submissions
    return []
            

@router.get("/certificates/{email}", response_model=List[Certificate])
async def get_certificates(request: Request, email: str = None):
    profile = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    if profile:
        certificate_ids = [ObjectId(certificate) for certificate in profile["Certificates"]]
        certificates = list(mongo_client.client.daspChatBotRating.Certificate.find({"_id": {"$in": certificate_ids}}))
        logger.debug(
            "get_certificates: {certificates}".format(
                certificates=", ".join(["{}".format(str(s)) for s in certificates])
            )
        )
        certificates = [Certificate.from_mongo(certificate) for certificate in certificates]
        return certificates
    return []

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(request: Request):
    profiles = mongo_client.client.daspChatBotRating.Profile.find({}, {"email": 1, "overallPoints": 1})
    profiles = [LeaderboardEntry.from_mongo(profile) for profile in profiles]
    
    leaderboard = [{"email": profile.email, "overallPoints": profile.overallPoints} for profile in profiles]

    return leaderboard

@router.get("/llms", response_model=List[LLM])
async def get_llms(request: Request):
    llms = list(mongo_client.client.daspChatBotRating.LLM.find({}))
    return [LLM.from_mongo(llm) for llm in llms]


@router.get("/badges/{email}", response_model=List[Badge])
async def get_badges(request: Request, email: str = None):
    profile = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    if profile:
        badge_ids = [ObjectId(badge) for badge in profile["Badges"]]
        badges = list(mongo_client.client.daspChatBotRating.Badge.find({"_id": {"$in": badge_ids}}))
        logger.debug(
            "get_badges: {badges}".format(
                badges=", ".join(["{}".format(str(badges)) for s in badges])
            )
        )
        badges = [Badge.from_mongo(badge) for badge in badges]
        return badges
    return []


@router.get("/llms/{email}", response_model=List[LLM])
async def get_llms_byemail(request: Request, email: str = None):
    profile = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    if profile:
        llm_ids = [ObjectId(llm) for llm in profile["availableModels"]]
        llms = list(mongo_client.client.daspChatBotRating.LLM.find({"_id": {"$in": llm_ids}}))
        logger.debug(
            "get_llms_byemail: {llms}".format(
                llms=", ".join(["{}".format(str(llms)) for s in llms])
            )
        )
        llms = [LLM.from_mongo(llm) for llm in llms]
        return llms
    return []

@router.get("/profiles/{email}", response_model=Profile)
async def get_profile(request: Request, email: str):
    profile_data = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Return the profile data as is (without resolving links)
    return Profile.from_mongo(profile_data)

@router.post("/badges", response_model=Badge)
async def add_badge(badge: Badge):
    badge_data = badge.dict(by_alias=True)  # `by_alias=True` ensures that aliases (like 'id' for '_id') are used

    # Check if the badge has a custom ID provided
    if not badge_data.get('id'):
        badge_data['_id'] = ObjectId()  # Generate new ObjectId if not provided
    else:
        badge_data['_id'] = badge_data.pop('id')  # Rename 'id' to '_id' for MongoDB compatibility

    # Check if a badge with the same ID already exists
    if mongo_client.client.daspChatBotRating.Badge.find_one({"_id": badge_data['_id']}):
        raise HTTPException(status_code=400, detail="Badge with this ID already exists")

    # Create the badge in the database
    new_badge = mongo_client.client.daspChatBotRating.Badge.insert_one(badge_data)

    # Retrieve the inserted badge to return it
    created_badge = mongo_client.client.daspChatBotRating.Badge.find_one({"_id": new_badge.inserted_id})

    if created_badge:
        return Badge.from_mongo(created_badge)
    raise HTTPException(status_code=500, detail="Badge creation failed")

@router.post("/profiles", response_model=Profile)
async def create_profile(profile: Profile):
    profile_data = profile.dict(by_alias=True)

    # Check if a profile with the same email already exists
    if mongo_client.client.daspChatBotRating.Profile.find_one({"email": profile_data['email']}):
        raise HTTPException(status_code=400, detail="Profile with this email already exists")

    # Default to empty lists if not provided
    profile_data.setdefault('certificates', [])
    profile_data.setdefault('badges', [])
    profile_data.setdefault('submissions', [])
    profile_data.setdefault('availableModels', [])
    # Create the profile in the database
    new_profile = mongo_client.client.daspChatBotRating.Profile.insert_one(profile_data)

    # Retrieve the inserted profile to return it
    created_profile = mongo_client.client.daspChatBotRating.Profile.find_one({"_id": new_profile.inserted_id})

    if created_profile:
        return Profile.from_mongo(created_profile)
    raise HTTPException(status_code=500, detail="Profile creation failed")

@router.post("/llms", response_model=LLM)
async def create_llm(llm: LLM):
    llm_data = llm.dict(by_alias=True)
    if not llm_data.get('id'):
        llm_data['_id'] = ObjectId()
    else:
        llm_data['_id'] = llm_data.pop('id')

    new_llm = mongo_client.client.daspChatBotRating.LLM.insert_one(llm_data)
    created_llm = mongo_client.client.daspChatBotRating.LLM.find_one({"_id": new_llm.inserted_id})

    if created_llm:
        return LLM.from_mongo(created_llm)
    raise HTTPException(status_code=500, detail="LLM creation failed")

@router.put("/profiles/{email}", response_model=Profile)
async def update_profile(email: str, profile: Profile):
    # Ensure the email in the request matches the email in the body
    if email != profile.email:
        raise HTTPException(status_code=400, detail="Email in URL and body must match")

    # Convert Pydantic model to dictionary and exclude unset fields
    profile_data = profile.dict(exclude_unset=True)

    # Update the database entry
    result = mongo_client.client.daspChatBotRating.Profile.replace_one(
        {"email": email},
        profile_data
    )

    # Check if the profile was found and updated
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Profile not updated")

    # Retrieve and return the updated profile
    updated_profile = mongo_client.client.daspChatBotRating.Profile.find_one({"email": email})
    return Profile.from_mongo(updated_profile)

@router.delete("/llms/{llm_id}", response_model=dict)
async def delete_llm(llm_id: str):
    result = mongo_client.client.daspChatBotRating.LLM.delete_one({"_id": ObjectId(llm_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="LLM not found")
    return {"status": "success", "message": "LLM deleted"}