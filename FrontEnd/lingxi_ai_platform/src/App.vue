<template>
    <!-- html -->
    <div class="app">
        <router-view></router-view>
    </div>
</template>

<script lang="ts">
    export default {
        name:'App'     // 根组件名
    }
</script>

<style>
    /*  样式  */
    .app {
        width: 100%;
        height: 100vh;
        margin: 0;
        padding: 0;
    }
    
    body {
        margin: 0;
        padding: 0;
    }
    
    #app {
        width: 100%;
        height: 100vh;
    }
</style>