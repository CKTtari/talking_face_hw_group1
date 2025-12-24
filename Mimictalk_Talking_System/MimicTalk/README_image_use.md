# MimicTalk容器镜像使用指南
## 导入镜像为容器：
将mimictalk.tar放到Mimictalk_Talking_System/MimicTalk/目录下
执行以下命令生成容器
docker load -i mimictalk.tar
docker compose up -d


## 运行问题
- dockerfile里写的各种依赖并不靠谱，构建后还需要很多操作解决冲突。不过你们应该也不需要重新构建，现在的容器就是我把很多问题都解决完的版本。
- 运行需要支持cuda12.1的显卡，windows docker需要下载ubuntu作为内核，docker desktop自带那个特供版wsl连不上显卡。
![alt text](image.png)
resource saver建议关闭
- 不过要是在服务器docker上就不一样了，我目前还都是用笔记本跑的。

## 目前已测试：
- 推理可用
- 可以启动gradio界面
## 未测试
- 训练模型
- gradio实际功能测试
## 后续工作
- 跑训练，复现模型
- 自己找素材进行推理，做成满足前端应用呈现的效果
- 数据集测评
- 模型结构剖析与改进

