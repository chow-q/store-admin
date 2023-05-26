from flask import Flask, request

app = Flask(__name__)

# 读取店铺列表
def read_store():
    with open('stores.txt', 'r',encoding='utf-8') as f:
        lines = f.readlines()
    store = {}
    for line in lines:
        # 把每一行按照空格划分为店铺名和 id
        name, id = line.strip().split(' ')
        # 存储到 store 字典中
        store[id] = name
    return store

# 保存店铺列表
def save_store(store):
    with open('stores.txt', 'w',encoding='utf-8') as f:
        for id, name in store.items():
            f.write('%s %s\n' % (name, id))

# 显示店铺列表
@app.route('/store', methods=['GET'])
def show_store():
    store = read_store()
    # 返回 HTML 页面
    return '''
        <html>
            <head>
                <title>直播回放店铺管理</title>
                <link rel="stylesheet" href="//unpkg.com/element-ui@2.15.13/lib/theme-chalk/index.css">
                
            </head>
            <body>
                <style>
                    table {
                        border: 1px solid black;
                        border-collapse: collapse;
                        padding: 5px;
                        margin: 0 auto; /*设置居中*/
                    }
                  th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    padding: 5px;
                    vertical-align: middle;
                    
                  }
                </style>
                <script src="//unpkg.com/vue@2/dist/vue.js"></script>
                <script src="//unpkg.com/element-ui@2.15.13/lib/index.js"></script>
                <script src="//unpkg.com/axios/dist/axios.min.js"></script>
                <div id="app">
                <h2>添加店铺</h2>
                <el-form :inline="true" :model="formInline" class="demo-form-inline">
                      <el-form-item label="店铺名">
                        <el-input v-model="formInline.name" placeholder="店铺名"></el-input>
                      </el-form-item>
                      <el-form-item label="店铺id">
                        <el-input v-model="formInline.id" placeholder="店铺id"></el-input>
                      </el-form-item>                  
                      <el-form-item>
                        <el-button type="primary" @click="openFullScreen1">添加</el-button>
                      </el-form-item>
                </el-form>                             
                <h2>取回归档视频</h2>
            
                <el-form :inline="true" :model="formInline" class="demo-form-inline">
                  <el-form-item label="推流id">
                    <el-input v-model="formInline.pushid" placeholder="推流id"></el-input>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="openFullScreen2">取回并下载归档视频</el-button>
                  </el-form-item>
                </el-form>

                <h2>店铺列表</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>店铺名</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        %s
                    </tbody>
                </table>
                </div>  
                <script>  
                var Main = {
                    data() {
                      return {
                        formInline: {
                          pushid: ''
                        }
                      }
                    },
                    methods: {
                      openFullScreen2() {
                              // 发送POST请求
                              axios.post('/store', {
                                pushid: this.formInline.pushid,
                                action:'get_video'
                                
                              })
                              .then(response => {
                                // 处理响应数据
                                console.log(response.data);
                                loading.close();
                                // 弹窗展示数据
                                this.$alert(response.data, '下载成功', {
                                  confirmButtonText: '确定',
                                  dangerouslyUseHTMLString: true
                                })
                              })
                              .catch(error => {
                                // 处理错误
                                console.error(error);
                              });
                              const loading = this.$loading({
                                  lock: true,
                                  text: '下载中',
                                  spinner: 'el-icon-loading',
                                  background: 'rgba(0, 0, 0, 0.7)'
                              });
                              setTimeout(() => {
                                  loading.close();
                              }, 20000);
                      },
                      openFullScreen1() {
                              // 发送POST请求
                              axios.post('/store', {
                                name: this.formInline.name,
                                id: this.formInline.id,
                                action:'add'                               
                              })
                              .then(response => {
                                // 处理响应数据
                              console.log(response.data);
                              // 弹窗展示数据
                                this.$alert(response.data, '店铺添加成功', {
                                  confirmButtonText: '确定',
                                  dangerouslyUseHTMLString: true
                                }).then(() => {
                                  location.reload();
                                });                            
                              })
                              .catch(error => {
                                // 处理错误
                                console.error(error);
                              });
                      }        
                    }                      
                }

                var Ctor = Vue.extend(Main)
                new Ctor().$mount('#app')    
                </script>       
                <hr/>
            </body>
        </html>
    ''' % '\n'.join(['<tr><td>%s</td><td>%s</td><td><form method="POST" action="/store"><input type="hidden" name="action" value="delete"/><input type="hidden" name="id" value="%s"/><button type="submit">删除</button></form></td></tr>' % (id, name, id) for id, name in store.items()])

# 处理店铺操作
@app.route('/store', methods=['POST'])
def handle_store():
    try:
        action=request.get_json()['action']
    except:
        action=request.form.get('action')
    store = read_store()
    if action == 'get_video':
        result=request.get_json()['pushid']

        print(result)
        return f"命令执行结果: {result}"
    if action == 'add':
        id = request.get_json()['id']
        name = request.get_json()['name']
        store[id] = name
        save_store(store)
        return name

    if action == 'delete':
            print(action)
            id = request.form.get('id')
            del store[id]
            save_store(store)
            return '''
                <html>
                    <head>
                        <title>删除店铺</title>
                    </head>
                    <body>
                        <p>成功删除店铺：（ID：%s）</p>
                        <a href="/store">返回店铺列表</a>
                    </body>
                </html>
            ''' % (id)
    else:
            return "参数有误"

if __name__ == '__main__':
    app.run()
