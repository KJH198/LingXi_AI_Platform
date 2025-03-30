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
        background-color: aliceblue;
        box-sizing: 0 0 10px;
        border-radius: 10px;
        padding: 20px;
        min-height: 100vh;
    }
</style>