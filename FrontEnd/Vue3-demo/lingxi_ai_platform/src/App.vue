<template>
    <!-- html -->
    <div class="app">
        <Login></Login>
    </div>
</template>

<script lang="ts">
    import Login from './components/Login.vue';  // 引入叶组件
    export default {
        name:'App',     // 根组件名
        components:{    // 注册叶组件
            Login
        }
    }
</script>

<style>
    /*  样式  */
    .app {
        background-color: aliceblue;
        box-sizing: 0 0 10px;
        border-radius: 10px;
        padding: 20px;
    }
</style>