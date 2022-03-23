---
sidebar_position: 2
---

# Get Started

We support two ways to use SQuARE:
1. 🌐 Get access to the existing QA Skills (and even deploy your Skill!) via our [demo page](https://square.ukp-lab.de/).
2. 💾 Or clone and install SQuARE to host services on a local machine.

👉 If you want to use the SQuARE public service online, you can refer to [Online Service](#Online-Service) for using the existing skills and refer to 
[Add New Skills](#Add-New-Skills) for adding new skills.

👉 If you want to deploy SQuARE locally yourself, please refer to [Local Installation](#Local-Installation).

<a name="Online-Service"></a>

## Online Service
Try out the on-the-go skills on the [demo page](https://square.ukp-lab.de/)! 
The existing skills include span-extraction, abstractive, multi-choice QA 
with contexts or without contexts (open QA based on retrieval).

![demo-page](../../static/img/skill_comparison.png)

<a name="Add-New-Skills"></a>

## Add New Skills

### Step 1: Hosting New Skills
- If you want to add new skills to the [public service](https://square.ukp-lab.de/), please follow the skill-package examples (e.g. [skills/qa-retrieve-span-skill](https://github.com/UKP-SQuARE/square-core/tree/master/skills/qa-retrieve-span-skill)) and submit yours via a [pull request](https://github.com/UKP-SQuARE/square-core/pulls). We will make it run after code review;
- It is also OK to host the skill yourself somewhere else. The only thing that matters here is to provide a URL and also match the argument formats.


### Step 2: Register the Skill
Go to your user profile and click on "My Skills" and "New" buttons. Fill out the form and link it to the hosted skills:

![link-skill](../../static/img/link_skill.png)


<a name="Local-Installation"></a>

## Local Installation
### Requirements
To run UKP-SQuARE locally, you need the following software:
* [docker](https://docs.docker.com/get-docker/)
* [docker-compose](https://docs.docker.com/compose/install/#install-compose)
* [ytt](https://carvel.dev/ytt/)
* [jq](https://stedolan.github.io/jq/download/)

### Install
Next change the `environment` to `local` and `os` to your operating system in the [config.yaml](https://github.com/UKP-SQuARE/square-core/tree/master/config.yaml). For installation we provide a script that takes care of the entire setup for you. After installing the previous [requirements](#requirements), simply run:
```bash
bash install.sh
```
### Run 
Finally, you can run the full system with docker-compose. Before doing so, you might want to reduce the number of models running depending on your resources. To do so, remove the respective services from the docker-compose.
```bash
docker-compose up -d
```
Check with `docker-compose logs -f` if all systems have started successfully. Once they are up and running go to [square.ukp-lab.local](https://square.ukp-lab.local).
👉 Accept that the browser cannot verify the certificate.
## Citation

Coming soon!

<!-- If you find this repository helpful, feel free to cite our publication 
[UKP-SQUARE: An Online Platform for Question Answering Research]():

```
@inproceedings{
}
``` -->
