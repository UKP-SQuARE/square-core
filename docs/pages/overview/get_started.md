# Get Started
<link rel="stylesheet" type="text/css" media="all" href="../../_static/custom.css" />

We support two ways to use SQuARE:
1. 🌐 Get access to the existing QA Skills (and even deploy your Skill!) via our [demo page](https://square.ukp-lab.de/);
2. 💾 Or clone and install SQuARE to host services on a local machine.

👉 If you want to use the SQuARE public service online, you can refer to [Online Service](#Online-Service) for using the existing skills and refer to 
[Add New Skills](#Add-New-Skills) for adding new skills.

👉 If you want to deploy SQuARE locally yourself, please refer to [Local Installation](#Local-Installation).

<a name="Online-Service"></a>
## Online Service
Try out the on-the-go skills on the [demo page](https://square.ukp-lab.de/)! 
The existing skills include span-extraction, abstractive, multi-choice QA 
with contexts or without contexts (open QA based on retrieval).

![demo-page](../../images/demo-page.png)

<a name="Add-New-Skills"></a>
## Add New Skills

### Step 1: Hosting New Skills
- If you want to add new skills to the [public service](https://square.ukp-lab.de/), please follow the skill-package examples (e.g. [skills/qa-retrieve-span-skill](skills/qa-retrieve-span-skill)) and submit yours via a [pull request](https://github.com/UKP-SQuARE/square-core/pulls). We will make it run after code review;
- It is also OK to host the skill yourself somewhere else. The only thing that matters here is to provide a URL and also match the argument formats.


### Step 2: Register the Skill
Go to your user profile and click on "My Skills" and "New" buttons. Fill out the form and link it to the hosted skills:

![link-skill](../../images/link_skill.png)


<a name="Local-Installation"></a>
## Local Installation
For local development, it's best to build the project with docker compose by running `docker compose build`.  
If you just want to use the current system, you can pull all images from docker hub with `docker compose pull`.  
And finally run `docker compose up -d` to start the system.  

### Environment Configuration
1. Create an `.env` file the datastore_api under `./datstore_api/.env`
    ```bash
    API_KEY=<YOUR_DATASTORE_API_KEY>
    ES_URL=http://datastore_es:9200
    FAISS_URL=http://localhost/api
    MODEL_API_URL=http://localhost/api
    ```
2. Create an `.env` file for the skills under `./skills/.env` with the following content:
    ```bash
    DATA_API_KEY=<YOUR_DATASTORE_API_KEY>
    SQUARE_API_URL=http://localhost/api
    ```

3. If you use the UI locally, please also update the .env file under `./square-frontend/.env.production` with the following content:
    ```bash
    VUE_APP_BACKEND_URL=http://localhost/api/backend
    VUE_APP_SKILL_MANAGER_URL=http://localhost/api/skill-manager
    ```

4. Note that you also have to update the `traefik` service in the `docker-compose.yaml` according to your setup. The above configuration assumes that your project is running on localhost. 


## Citation

Coming soon!

<!-- If you find this repository helpful, feel free to cite our publication 
[UKP-SQUARE: An Online Platform for Question Answering Research]():

```
@inproceedings{
}
``` -->