<template>
    <div :class='["message", { dark }]'>
        <!-- bold text -->
        <strong>{{ author }}</strong>
        <br />
        {{text}}
    </div>
</template>

<script>

export default {
name: 'MessageView',
    props: [
        'text', // Content of the message
        'author', // Author of the message
        'dark' // Background variant of the box
    ]
}
</script>

<style scoped>
.message {
    background: #e7e7e7;
    border-radius: 10px;
    padding: 0.77rem;
    width: fit-content;
}

.message.dark {
    background: #5fc9f8;
}
</style>
