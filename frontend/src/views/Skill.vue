<!-- The Page of a Skill. The user can edit an existing skill or create a new skill here. -->
<template>
  <form v-on:submit.prevent="onSubmit">
    <Card :title="originalName ? originalName : 'New skill'">
      <template #leftItem>
        <router-link to="/skills" class="btn btn-outline-danger d-inline-flex align-items-center" role="button">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor"
            class="bi bi-caret-left-square" viewBox="0 0 16 16">
            <path
              d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z" />
            <path
              d="M10.205 12.456A.5.5 0 0 0 10.5 12V4a.5.5 0 0 0-.832-.374l-4.5 4a.5.5 0 0 0 0 .748l4.5 4a.5.5 0 0 0 .537.082z" />
          </svg>
          &nbsp;My skills
        </router-link>
      </template>
      <template #rightItem>
        <button class="btn btn-outline-danger d-inline-flex align-items-center" type="submit">
          <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-save"
            viewBox="0 0 16 16">
            <path
              d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z" />
          </svg>
          &nbsp;Save
        </button>
      </template>
      <Alert v-if="success" class="alert-success" dismissible>Skill was updated successfully.</Alert>
      <Alert v-if="failure" class="alert-danger" dismissible>An error occurred</Alert>
      <div class="row">
        <div class="col-md-6 mt-3">
          <label for="name" class="form-label">Skill name</label>
          <input v-model="skill.name" type="text" class="form-control" id="name" placeholder="Skill name">
        </div>

        <div class="col-md-3 mt-3">
          <label for="skillType" class="form-label">Skill type</label>
          <select v-model="skill.skill_type" class="form-select" id="skillType">
            <option v-for="skillType in skillTypes" v-bind:value="skillType" v-bind:key="skillType">
              {{ skillType }}
            </option>
          </select>
        </div>

        <div class="col-md-3 mt-5">
          <div class="form-check form-switch">
            <input v-model="skill.skill_settings.requires_context" v-bind:value="skill.skill_settings.requires_context"
              class="form-check-input" type="checkbox" role="switch" id="requiresContext">

            <label class="form-check-label" for="requiresContext"
              content="If the Skill requires a question and a passage/context as input, please activate this switch."
              v-tippy>
            <!-- <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor"
                class="bi bi-card-text" viewBox="0 0 16 16">
                <path
                  d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h13zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z" />
                <path
                  d="M3 5.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 8a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 8zm0 2.5a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5z" />
                                                                                                                                                      </svg> -->
              Requires context
            </label>
          </div>
        </div>


      </div>

      <div class="row">
        <div class="col-6 mt-3">
          <label for="datasets" class="form-label">Skill Datasets</label>
          <multiselect v-model="skill.data_sets" :options="dataSets" :multiple="true" :close-on-select="false"
            placeholder="Select a dataset"></multiselect>
          <small class="text-muted">Select the dataset on which the Skill was trained.</small>
        </div>


        <div class="col-6 mt-3">
          <label for="url_select" class="form-label">Skill URL</label>
          <select class="form-select" v-model="url" aria-label="Default select example" id="url_select">
            <option v-for="url in avail_urls" v-bind:key="url" :value="url">{{ url }} </option>
            <option value="Externally hosted">Externally hosted</option>
          </select>
          <small class="text-muted">URL to the hosted skill</small>

          <div v-if="url == 'Externally hosted'">
            <div class="row">
              <div class="col-6 mt-3">
                <input v-model="extern_url" type="url" class="form-control form-control-sm" id="url"
                  placeholder="http://...">
                <small class="text-muted">URL to the hosted skill (<span class="text-info">scheme</span>://<span
                    class="text-info">host</span>:<span class="text-info">port</span>/<span
                    class="text-info">base_path</span>)</small>
              </div>

              <div class="col-1 mt-3">
                <Status :url="extern_url" />
              </div>
            </div>

          </div>
        </div>
      </div>

      <div class="row mt-2">
        <div class="col-md-6">
          <div class="form-check form-switch">
            <input v-model="skill.published" v-bind:value="skill.published" class="form-check-input" type="checkbox"
              role="switch" id="published">
            <label class="form-check-label d-inline-flex align-items-center" for="published">
              <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" fill="currentColor" class="bi bi-globe"
                viewBox="0 0 16 16">
                <path
                  d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-6.923c-.67.204-1.335.82-1.887 1.855A7.97 7.97 0 0 0 5.145 4H7.5V1.077zM4.09 4a9.267 9.267 0 0 1 .64-1.539 6.7 6.7 0 0 1 .597-.933A7.025 7.025 0 0 0 2.255 4H4.09zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a6.958 6.958 0 0 0-.656 2.5h2.49zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5H4.847zM8.5 5v2.5h2.99a12.495 12.495 0 0 0-.337-2.5H8.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5H4.51zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5H8.5zM5.145 12c.138.386.295.744.468 1.068.552 1.035 1.218 1.65 1.887 1.855V12H5.145zm.182 2.472a6.696 6.696 0 0 1-.597-.933A9.268 9.268 0 0 1 4.09 12H2.255a7.024 7.024 0 0 0 3.072 2.472zM3.82 11a13.652 13.652 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5H3.82zm6.853 3.472A7.024 7.024 0 0 0 13.745 12H11.91a9.27 9.27 0 0 1-.64 1.539 6.688 6.688 0 0 1-.597.933zM8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855.173-.324.33-.682.468-1.068H8.5zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.65 13.65 0 0 1-.312 2.5zm2.802-3.5a6.959 6.959 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5h2.49zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7.024 7.024 0 0 0-3.072-2.472c.218.284.418.598.597.933zM10.855 4a7.966 7.966 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4h2.355z" />
              </svg>
              &nbsp; Public Skill &nbsp;
              <svg
                content="Select this if you want your skill to be publicly available for any user. If unselected, the skill will only be available to you."
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </label>
          </div>
        </div>

        <div class="col-md-6">
          <div class="form-check form-switch">
            <input v-model="skill.meta_skill" v-bind:value="skill.meta_skill" class="form-check-input" type="checkbox"
              role="switch" id="metaskill">
            <label class="form-check-label d-inline-flex align-items-center" for="metaskill">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-boxes"
                viewBox="0 0 16 16">
                <path
                  d="M7.752.066a.5.5 0 0 1 .496 0l3.75 2.143a.5.5 0 0 1 .252.434v3.995l3.498 2A.5.5 0 0 1 16 9.07v4.286a.5.5 0 0 1-.252.434l-3.75 2.143a.5.5 0 0 1-.496 0l-3.502-2-3.502 2.001a.5.5 0 0 1-.496 0l-3.75-2.143A.5.5 0 0 1 0 13.357V9.071a.5.5 0 0 1 .252-.434L3.75 6.638V2.643a.5.5 0 0 1 .252-.434L7.752.066ZM4.25 7.504 1.508 9.071l2.742 1.567 2.742-1.567L4.25 7.504ZM7.5 9.933l-2.75 1.571v3.134l2.75-1.571V9.933Zm1 3.134 2.75 1.571v-3.134L8.5 9.933v3.134Zm.508-3.996 2.742 1.567 2.742-1.567-2.742-1.567-2.742 1.567Zm2.242-2.433V3.504L8.5 5.076V8.21l2.75-1.572ZM7.5 8.21V5.076L4.75 3.504v3.134L7.5 8.21ZM5.258 2.643 8 4.21l2.742-1.567L8 1.076 5.258 2.643ZM15 9.933l-2.75 1.571v3.134L15 13.067V9.933ZM3.75 14.638v-3.134L1 9.933v3.134l2.75 1.571Z" />
              </svg>
              &nbsp; Meta-Skill &nbsp;
              <svg
                content="Meta-Skills are Skills that combine two or more Skills. Currently, TWEAC (routing), Meta-QA (fusion of predictions), and average of adapter werights are supported."
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 16 16">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </label>
          </div>
        </div>
      </div>


      <div class="row">
        <div class="col mt-3">
          <label for="description" class="form-label">Description</label>
          <input v-model="skill.description" type="text" class="form-control" id="description" placeholder="Description">
        </div>
      </div>

      <div class="row">
        <div class="col mt-4">
          <h3>Provide the arguments of the Skill</h3>
        </div>
      </div>

      <div class="row"
        v-if="skill.url != 'http://extractive-metaqa' && url != 'http://multiple-choice-metaqa' && url != 'http://metaqa'">
        <div class="col-md-6">
          <label for="base_model" class="form-label">Base Model
            <small class="text-muted">(leave empty if not required)
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle"
                viewBox="0 0 20 20">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </small>
          </label>
          <input v-if="skill.skill_type != 'information-retrieval'" type="text" v-model="skill_args.base_model"
            class="form-control form-control-sm" id="base_model" placeholder="UKP-SQuARE/distilroberta-squad">
          <input v-if="skill.skill_type == 'information-retrieval'" type="text" v-model="skill_args.base_model"
            class="form-control form-control-sm" id="base_model">
        </div>

        <div class="col-md-6">
          <input class="form-check-input" type="checkbox" id="adapter_flag" v-model="adapter_flag"
            :disabled="skill_args.base_model == ''">
          <label for="adapter" class="form-label">
            &nbsp;Use Adapter
            <small class="text-muted">
              <svg content="Check this box if your base model must use adapters, and write the name of the adapter below."
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 20 20">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
              &nbsp;
            </small>
          </label>
          &nbsp;
          <input class="form-check-input" type="checkbox" id="average_adapters_flag" v-model="average_adapters" value="1"
            :disabled="!adapter_flag">
          <label class="form-check-label" for="average_adapters_flag">
            &nbsp; Combine Adapters
            <small class="text-muted">
              <svg
                content="(Advanced!) If you want to combine multiple adapters by averaging their weights as in (Friedman et al., EMNLP 2021), select 'Use Adapter' and 'Combine Adapters' and write the list of adapters below. (press enter after each adapter). Do not select this if unsure."
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 20 20">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
              <a href="https://aclanthology.org/2021.emnlp-main.495.pdf">More info</a>
            </small>
          </label>
          <input v-if="!average_adapters" type="text" v-model="skill_args.adapter" class="form-control form-control-sm"
            id="adapter" :disabled="!adapter_flag" placeholder="AdapterHub/bert-base-uncased-pf-squad">
          <vue-tags-input v-if="average_adapters" class="form-control form-control-sm" id="multiple_adapters_input"
            style="max-width: unset;" v-model="auxAdapter" :tags="list_adapters"
            @tags-changed="newAdapter => list_adapters = newAdapter" />
        </div>
      </div>

      <!-- MetaQA Input -->
      <div class="row"
        v-if="url == 'http://extractive-metaqa' || url == 'http://multiple-choice-metaqa' || url == 'http://metaqa'">
        <div class="col-md-6">
          <label for="base_model" class="form-label">MetaQA Model</label>
          <input type="text" v-model="skill_args.base_model" class="form-control form-control-md" id="base_model"
            placeholder="haritzpuerto/MetaQA">
        </div>

        <div class="col-md-6">
          <label for="datasets" class="form-label">MetaQA's Agents</label>
          <multiselect v-model="metaqa_agents" :options="list_skills_names" :multiple="true" :close-on-select="false"
            placeholder="Select the skills"></multiselect>
          <small class="text-muted">Select the Skills in the same order as MetaQA was trained.</small>
        </div>

      </div>

      <div class="row"
        v-if="skill.url != 'http://extractive-metaqa' || url == 'http://multiple-choice-metaqa' || url == 'http://metaqa'">
        <div class="col-md-6">
          <div>
            <label for="datastore" class="form-label">Datastore
              <small class="text-muted">(leave empty if not required)
                <svg
                  content="If your Skill requires the use of a datastore (i.e., a document collection) because
                                                                                                                                                        it is an open-domain Skill, write the name of the datastore here.
                                                                                                                                                         eg: 'bioasq' Leave blank if unsure"
                  v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                  class="bi bi-info-circle" viewBox="0 0 20 20">
                  <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                  <path
                    d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
                </svg>
              </small>
            </label>
            <select v-model="skill_args.datastore" class="form-select form-select-sm" id="datastore">
              <option v-for="datastore in datastores" v-bind:value="datastore" v-bind:key="datastore">
                {{ datastore }}
              </option>
            </select>
          </div>
        </div>
        <div class="col-md-6">
          <label for="index" class="form-label">Index
            <small class="text-muted">(leave empty if not required)
              <svg
                content="If your Skill is using a datatore and you do not want to use the predefined index (i.e., bm25),
                                                                                                                                                        write the name of the index here.
                                                                                                                                                         eg: 'distilbert'. If you selected 'requires context', then you do not need a datastore. Leave blank if unsure"
                v-tippy xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
                class="bi bi-info-circle" viewBox="0 0 20 20">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </small>
          </label>
          <select v-model="skill_args.index" class="form-select form-select-sm" id="index">
            <option v-for="index in indices" v-bind:value="index" v-bind:key="index">
              {{ index }}
            </option>
          </select>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <label for="other_args" class="form-label">Others
            <small
              content="Write any other additional argument you may need. The text should be a json document (i.e., {'key': 'value'}) Leave blank if unsure"
              v-tippy class="text-muted">(leave empty if not required)
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-info-circle"
                viewBox="0 0 20 20">
                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z" />
                <path
                  d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z" />
              </svg>
            </small>
          </label>
          <input type="text" v-model="skill_args.others" class="form-control form-control-sm" id="other_args">
        </div>
      </div>

      <div class="row">
        <div class="col mt-4">
          <h3>Provide example questions</h3>
          <p class="mb-1">These examples will be featured alongside your skill.</p>
        </div>
      </div>
      <div v-for="(example, index) in skill.skill_input_examples" v-bind:key="index" class="row">
        <h4 class="mt-3">Example {{ index + 1 }}</h4>
        <div class="col-md mt-2">
          <label :for="`question${index}`" class="form-label">Question</label>
          <textarea v-model="example.query" class="form-control mb-2" style="resize: none;"
            :style="{ 'height': `${38 * (skill.skill_settings.requires_context ? 3 : 1)}px` }" :id="`question${index}`"
            placeholder="Question" />
        </div>
        <div v-if="skill.skill_settings.requires_context" class="col-md mt-2">
          <label :for="`context${index}`" class="form-label">Context</label>
          <textarea v-model="example.context" class="form-control mb-2" style="resize: none; height: calc(38px * 3);"
            :id="`context${index}`" placeholder="Context" />
        </div>

        <div v-if="skill.skill_type == 'multiple-choice'" class="col-md mt-2">
          <label for="choices_loop" class="form-label">Write at least 2 answer choices.</label>
          <div class="row g-0" v-for="(choice, choice_idx) in list_answer_choices[index]" :key="choice_idx"
            id="choices_loop">
            <div class="col-sm">
              <div class="input-group input-group-sm mb-3">
                <span class="input-group-text" id="basic-addon1">{{ choice_idx + 1 }}</span>
                <input v-model="list_answer_choices[index][choice_idx]" type="text" class="form-control form-control-sm">
              </div>
            </div>
          </div>
          <!-- button to add one more element to list_choices -->
          <div class="form-inline">
            <button type="button" class="btn btn-sm btn-outline-success" v-on:click="addChoice(index)">Add
              Choice</button>
            <!-- button to remove one element of list_choices -->
            <button type="button" class="btn btn-sm btn-outline-danger" v-on:click="removeChoice(index)">Remove
              Choice</button>
          </div>
        </div>
      </div>
    </Card>
  </form>
</template>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<script>
import Vue from 'vue'

import Alert from '@/components/Alert.vue'
import Card from '@/components/Card.vue'
import Status from '@/components/Status.vue'
import { getSkill, getSkills, getSkillTypes, getDataSets, getDatastoreIndices, getDatastores } from '@/api'

import VueTippy from "vue-tippy";
Vue.use(VueTippy);

import Multiselect from 'vue-multiselect'
import VueTagsInput from '@johmun/vue-tags-input';



export default Vue.component('edit-skill', {
  data() {
    return {
      skillTypes: [],
      dataSets: [],
      datastores: [],
      indices: [],
      url: '',
      extern_url: '', // skill.url will be overwritten by this value if it is not empty
      avail_urls: [],
      // adapters
      adapter_flag: false,
      average_adapters: false,
      list_adapters: [],
      // metaqa
      list_skills: [],
      list_skills_names: [],
      metaqa_agents: [],
      auxAdapter: "",
      skill: {
        name: '',
        skill_type: '',
        data_sets: [],
        description: '',
        skill_settings: {
          requires_context: false,
          requires_multiple_choices: 0
        },
        url: '',
        default_skill_args: null,
        user_id: '',
        published: true,
        meta_skill: false,
        skill_input_examples: []
      },
      skill_args: {
        base_model: '',
        adapter: '',
        datastore: '',
        index: '',
        others: ''
      },
      /**
       * The name for the title.
       * We do not use skill.name for this so that the title is only changed when the user updates the skill.
       */
      originalName: '',
      success: false,
      failure: false,
      stringifiedJSON: '',
      validJSON: true,
      numberSkillExamples: 3,
      list_answer_choices: [["", ""], ["", ""], ["", ""]]
    }
  },
  components: {
    Alert,
    Card,
    Status,
    Multiselect,
    VueTagsInput
  },
  computed: {
    /**
     * Decides if we want to create a new skill or edit an existing skill
     */
    isCreateSkill() {
      return this.$route.params.id === 'new_skill'
    },
    skillArguments: {
      // Use intermediate stringified variable to not interrupt the users typing
      get: function () {
        return this.stringifiedJSON
      },
      set: function (newValue) {
        this.stringifiedJSON = newValue
        try {
          if (newValue.length > 0) {
            this.skill.default_skill_args = JSON.parse(newValue)
          } else {
            this.skill.default_skill_args = null
          }
          this.validJSON = true
        } catch (e) {
          this.validJSON = false
        }
      }
    },
  },
  methods: {
    onSubmit() {
      if (this.isCreateSkill) {
        this.createSkill()
      } else {
        this.updateSkill()
      }
    },
    updateSkill() {
      this.success = false
      // if skill type is multiple-choice, add the list_answer_choices to the skill_input_examples
      if (this.skill.skill_type == 'multiple-choice') {
        for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
          this.skill.skill_input_examples[i]['choices'] = this.list_answer_choices[i]
        }
      }
      // add arguments to skill
      this.addSkillArgs2Skill()
      // update skill
      this.$store
        .dispatch('updateSkill', { skill: this.skill })
        .then(() => {
          this.originalName = this.skill.name
          this.success = true
          this.failure = false
        })
        .catch(() => {
          this.failure = true
        })
    },
    createSkill() {
      // if skill type is multiple-choice, add the list_answer_choices to the skill_input_examples
      if (this.skill.skill_type == 'multiple-choice') {
        for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
          this.skill.skill_input_examples[i]['choices'] = this.list_answer_choices[i]
        }
      }
      this.skill.url = this.url
      // if extern url is not empty, overwrite skill.url
      if (this.url == 'Externally hosted' && this.extern_url != '') {
        this.skill.url = this.extern_url
      }
      // add arguments to skill
      this.addSkillArgs2Skill()
      if (this.skill.url == 'http://extractive-metaqa' || this.skill.url == 'http://multiple-choice-metaqa' || this.skill.url == 'http://metaqa') {
        this.addSkillAgents()
      }
      // create skill
      this.$store
        .dispatch('createSkill', { skill: this.skill })
        .then(() => this.$router.push('/skills'))
        .catch(() => {
          this.failure = true
        })
    },
    addSkillArgs2Skill() {
      this.skill.default_skill_args = {}
      if (this.skill_args.base_model != '') {
        this.skill.default_skill_args = { 'base_model': this.skill_args.base_model }
      }
      this.skill.default_skill_args['average_adapters'] = this.average_adapters
      if (this.skill.default_skill_args['average_adapters']) {
        this.skill.default_skill_args['adapter'] = []
        for (let i = 0; i < this.list_adapters.length; i++) {
          this.skill.default_skill_args['adapter'].push(this.list_adapters[i]['text'])
        }
      } else {
        if (this.skill_args.adapter != '') {
          this.skill.default_skill_args['adapter'] = this.skill_args.adapter
        }
      }
      if (this.skill_args.datastore != '') {
        this.skill.default_skill_args['datastore'] = this.skill_args.datastore
      }
      if (this.skill_args.index != '') {
        // BM25 is the default index
        if (this.skill_args.index == 'BM25') {
          this.skill.default_skill_args['index'] = ""
        } else {
          this.skill.default_skill_args['index'] = this.skill_args.index
        }
      }
      // skill args is a json. add the key value pairs to the skill args
      if (this.skill_args.others != '') {
        try {
          var others = JSON.parse(this.skill_args.others)
          for (var key in others) {
            this.skill.default_skill_args[key] = others[key]
          }
        } catch (e) {
          this.validJSON = false
        }
      }

    },
    addSkillAgents() {
      this.skill.default_skill_args['list_skills'] = []
      // filter list_skills for skills with names in list_agents
      this.list_skills.filter(skill => this.metaqa_agents.includes(skill.name)).forEach(skill => {
        this.skill.default_skill_args['list_skills'].push(skill.id)
      })

    },
    addInputExampleFields() {
      // Dynamically add input fields
      // In case the default amount is modified later this will adapt for legacy skills
      while (this.skill.skill_input_examples.length < this.numberSkillExamples) {
        this.skill.skill_input_examples.push({ 'query': '', 'context': '' })
      }
    },
    setSelectIndices() {
      getDatastoreIndices(this.$store.getters.authenticationHeader(), this.skill_args.datastore)
        .then((response) => {
          this.indices.push("BM25")
          // iterate over the indices and add the name to the list
          for (let i = 0; i < response.data.length; i++) {
            this.indices.push(response.data[i].name)
          }
        })
    },
    addChoice(index) {
      this.list_answer_choices[index].push("")
    },
    removeChoice(index) {
      if (this.list_answer_choices[index].length > 2) {
        this.list_answer_choices[index].pop()
      } else {
        alert("You must have at least 2 choices.")
      }
    },
    setSkillURL() {
      if (this.skill.meta_skill) {
        this.avail_urls = ["http://extractive-metaqa", "http://multiple-choice-metaqa", "http://metaqa", "http://tweac"]
      } else {
        this.avail_urls = []
        switch (this.skill.skill_type) {
          case 'abstractive':
            this.url = 'http://generative-qa'
            this.avail_urls.push('http://generative-qa')
            break
          case 'span-extraction':
            if (this.skill.skill_settings.requires_context) {
              this.url = 'http://extractive-qa'
              this.avail_urls.push('http://extractive-qa')
            }
            else {
              this.url = 'http://open-extractive-qa'
              this.avail_urls.push('http://open-extractive-qa')
            }
            this.avail_urls.push('http://metaqa')
            this.avail_urls.push('http://tweac')
            break
          case 'multiple-choice':
            this.url = 'http://multiple-choice-qa'
            this.avail_urls.push('http://multiple-choice-qa')
            this.avail_urls.push('http://metaqa')
            this.avail_urls.push('http://tweac')
            break
          case 'categorical':
            this.url = 'http://multiple-choice-qa'
            this.avail_urls.push('http://multiple-choice-qa')
            break
          case 'information-retrieval':
            this.url = 'http://information-retrieval'
            this.avail_urls.push('http://information-retrieval')
            break
          default:
            break
        }
      }
    }
  },
  watch: {
    'skill.skill_type'() {
      this.setSkillURL()
    },
    'skill.skill_settings.requires_context'() {
      this.setSkillURL()
    },
    'skill_args.datastore'() {
      this.indices = []
      this.setSelectIndices()
    },
    'url'() {
      if (this.url == 'http://tweac' || this.url == 'http://extractive-metaqa' || this.url == 'http://multiple-choice-metaqa' || this.url == 'http://metaqa') {
        this.skill.meta_skill = true
        if (this.url == 'http://tweac') {
          this.skill_args.others = '{"max_skills_per_dataset": 2}'
        }
      } else {
        this.skill.meta_skill = false
      }
    },
    'skill.meta_skill'() {
      this.setSkillURL()
    },
    'average_adapters'() {
      this.skill.meta_skill = this.average_adapters
    }
  },
  beforeMount() {
    getSkillTypes(this.$store.getters.authenticationHeader())
      .then((response) => {
        this.skillTypes = response.data
      })
    getDataSets(this.$store.getters.authenticationHeader())
      .then((response) => {
        for (let item_dataset = 0; item_dataset < response.data.length; item_dataset++) {
          this.dataSets.push(response.data[item_dataset].name);
        }
      })
    getDatastores(this.$store.getters.authenticationHeader())
      .then((response) => {
        this.datastores.push("None")
        // iterate over the datastores and add the name to the list
        for (let i = 0; i < response.data.length; i++) {
          this.datastores.push(response.data[i].name)
        }
      })
    getSkills(this.$store.getters.authenticationHeader())
      .then((response) => {
        // iterate over the skills and add the name to the list
        for (let i = 0; i < response.data.length; i++) {
          this.list_skills.push(response.data[i])
          this.list_skills_names.push(response.data[i].name)
        }
      })
    if (!this.isCreateSkill) {
      getSkill(this.$store.getters.authenticationHeader(), this.$route.params.id)
        .then((response) => {
          let data = response.data
          if (data.skill_input_examples == null) {
            data.skill_input_examples = []
          }
          this.skill = data
          this.url = this.skill.url
          this.originalName = this.skill.name
          // add skill args to the UI
          this.skill_args.base_model = this.skill.default_skill_args['base_model']
          // adding adapters
          if (this.skill.default_skill_args['average_adapters']) {
            this.adapter_flag = true
            this.average_adapters = true
            this.list_adapters = []
            for (let i = 0; i < this.skill.default_skill_args['adapter'].length; i++) {
              this.list_adapters.push({ 'text': this.skill.default_skill_args['adapter'][i] })
            }
          } else {
            this.average_adapters = false
            this.skill_args.adapter = this.skill.default_skill_args['adapter']
            this.list_adapters = [{ 'text': this.skill.default_skill_args['adapter'] }] // just in case the use wants to change to average adapters
            if (this.skill_args.adapter != null && this.skill_args.adapter != '') {
              this.adapter_flag = true
            } else {
              this.adapter_flag = false
            }
          }
          // adding metaqa agents
          getSkills(this.$store.getters.authenticationHeader()) // get the list of skills again
            .then((response) => {
              // iterate over the skills
              for (let i = 0; i < response.data.length; i++) {
                //if id in this.skill.default_skill_args['list_skills'] then add to metaqa_agents
                if (this.skill.default_skill_args['list_skills'].includes(response.data[i].id)) {
                  this.metaqa_agents.push(response.data[i].name)
                }
              }
            })




          // adding datastore
          this.skill_args.datastore = this.skill.default_skill_args['datastore']
          if (this.skill_args.datastore !== '' && this.skill.default_skill_args['index'] == '') {
            this.skill_args.index = 'BM25'
          } else {
            this.skill_args.index = this.skill.default_skill_args['index']
          }
          // add the rest of the skill args to the others field
          var others = {}
          for (var key in this.skill.default_skill_args) {
            if (key != 'base_model' && key != 'adapter' && key != 'datastore' && key != 'index' && key != 'average_adapters' && key != 'list_skills') {
              others[key] = this.skill.default_skill_args[key]
            }
          }
          // if others is empty, set it to empty string
          if (Object.keys(others).length === 0) {
            others = ''
          } else {
            this.skill_args.others = JSON.stringify(others)
          }
          // this.skillArguments = JSON.stringify(this.skill.default_skill_args)
          this.addInputExampleFields()
          if (this.skill.skill_input_examples[0].choices !== null) {
            // for each skill_input_example, add the choices to the list_answer_choices
            for (let i = 0; i < this.skill.skill_input_examples.length; i++) {
              this.list_answer_choices[i] = this.skill.skill_input_examples[i]['choices']
            }
            if (this.list_answer_choices.length < this.numberSkillExamples) {
              for (let i = this.list_answer_choices.length; i < this.numberSkillExamples; i++) {
                this.list_answer_choices.push(["", ""])
              }
            }
          }
          // for the transition period between old format of answer choices and the new one
          if (this.skill.skill_input_examples[0].choices == null && this.skill.skill_type == 'multiple-choice') {
            this.list_answer_choices = [["", ""], ["", ""], ["", ""]]
          }

        })
    } else {
      this.addInputExampleFields()
    }
    this.skill.user_id = this.$store.state.userInfo.preferred_username
  }
})
</script>

<style lang="css">
/* style the background and the text color of the input ... */

.vue-tags-input .ti-input {
  padding: 0px 0px;
  border: 0px;
}

.vue-tags-input .ti-tag {
  padding: 0px 5px;
}

.vue-tags-input .ti-new-tag-input-wrapper {
  margin: 0px;
}
</style>
