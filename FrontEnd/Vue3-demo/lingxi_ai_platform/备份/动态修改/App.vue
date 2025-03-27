<template>
    <!-- html -->
    <div class="app">
        <h1> 这是根页面 </h1>
        <Person></Person>
    </div>
</template>

<script lang="ts">
    import Person from './components/Person.vue';
    export default {
        name:'App',     // 根组件名
        components:{    // 注册叶组件
            Person
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