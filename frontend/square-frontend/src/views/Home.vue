<template>
    <b-container>
        <b-nav tabs fill align="center" class="mb-2"> 
            <b-nav-item to="/" exact exact-active-class="active" >Question</b-nav-item>
            <b-nav-item to="/results" exact exact-active-class="active">Answers</b-nav-item>
        </b-nav>
        <router-view></router-view>
    </b-container>
</template>

<script>
export default {
  name: "home"
}
</script>