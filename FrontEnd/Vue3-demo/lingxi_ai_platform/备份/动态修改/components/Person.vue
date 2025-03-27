<template>
    <!-- html -->
    <div class="persion">  <!-- 类名 -->
        <h1> 这是叶子页面 </h1>
        <p>姓名:{{name}}</p>
        <p>年龄:{{age}}</p>
        <button @click="changeName">修改名字</button>
        <button @click="changeAge">修改年龄</button>
        <button @click="showTel">查看联系方式</button>
    </div>
</template>

<script lang="ts" setup name="Persion">
    import { ref } from 'vue'

    // setup
    let name = ref('张三')   //这里不是响应式
    let age = ref(18)
    let tel = ref('123456789')

    function changeName(){  // name改了,但不能响应
        name.value += '1'
        console.log(name)
    }
    function changeAge(){
        age.value += 5
    }
    function showTel(){
        alert(tel.value)
    }
</script>

<style>
    /*  样式  */
    .persion {
        background-color: rgb(254, 255, 240);
        box-sizing: 0 0 10px;
        border-radius: 10px;
        padding: 20px;
    }
    button {
        margin: 0 5px;
    }
</style>