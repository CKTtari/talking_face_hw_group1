 容器内日志：cpb: bitrate max/min/avg: 0/0/200000 buffer size: 0 vbv_delay: N/A
📝 容器内日志：frame=  132 fps=0.0 q=1.0 size=N/A time=00:00:05.60 bitrate=N/A speed=11.2x
📝 容器内日志：frame=  261 fps=261 q=1.0 size=N/A time=00:00:10.76 bitrate=N/A speed=10.8x
📝 容器内日志：frame=  395 fps=263 q=1.0 size=N/A time=00:00:16.12 bitrate=N/A speed=10.7x
📝 容器内日志：[out#0/image2 @ 0x5658551c5dc0] video:23486KiB audio:0KiB subtitle:0KiB other streams:0KiB global headers:0KiB muxing overhead: unknown
📝 容器内日志：frame=  500 fps=264 q=1.0 Lsize=N/A time=00:00:20.00 bitrate=N/A speed=10.6x
📝 容器内日志：| python data_gen/utils/process_video/extract_segment_imgs.py --ds_name=nerf --vid_dir=data/raw/videos/train_4b140be704c948c8adf4d182672e271c.mp4 --force_single_process
📝 容器内日志：todo videos number: 1
📝 容器内日志：WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
📝 容器内日志：I0000 00:00:1766496937.591663   32143 task_runner.cc:85] GPU suport is not available: INTERNAL: ; RET_CHECK failure (mediapipe/gpu/gl_context_egl.cc:84) egl_initializedUnable to initialize EGL
📝 容器内日志：INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
📝 容器内日志：W0000 00:00:1766496937.703565   32164 inference_feedback_manager.cc:114] Feedback manager requires a model with a single signature inference. Disabling support for feedback tensors.
📝 容器内日志：/opt/conda/envs/mimictalk/lib/python3.9/site-packages/mediapipe/tasks/python/vision/image_segmenter.py:158: UserWarning: MessageFactory class is deprecated. Please use GetMessageClass() instead of MessageFactory.GetPrototype. MessageFactory class will be removed after 2024.
📝 容器内日志：graph_config = self._runner.get_graph_config()
📝 容器内日志：| Extracting Segmaps && Saving...
📝 容器内日志：
📝 容器内日志：generating segment images in single-process...:   0%|          | 0/500 [00:00<?, ?it/s]
📝 容器内日志：generating segment images in single-process...:   0%|          | 1/500 [00:00<02:15,  3.69it/s]
📝 容器内日志：generating segment images in single-process...:   0%|          | 2/500 [00:00<02:01,  4.08it/s]
📝 容器内日志：generating segment images in single-process...:   1%|          | 3/500 [00:00<01:59,  4.17it/s]
📝 容器内日志：generating segment images in single-process...:   1%|          | 4/500 [00:00<01:57,  4.21it/s]
📝 容器内日志：generating segment images in single-process...:   1%|          | 5/500 [00:01<01:58,  4.17it/s]
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 268, in __call__
    await wrap(partial(self.listen_for_disconnect, receive))
  File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 264, in wrap
    await func()
  File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 233, in listen_for_disconnect
    message = await receive()
  File "E:\.conda\talking_face\lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 531, in receive
    await self.message_event.wait()
  File "E:\.conda\talking_face\lib\asyncio\locks.py", line 309, in wait
    await fut
asyncio.exceptions.CancelledError

During handling of the above exception, another exception occurred:

  + Exception Group Traceback (most recent call last):
  |   File "E:\.conda\talking_face\lib\site-packages\uvicorn\protocols\http\h11_impl.py", line 403, in run_asgi
  |     result = await app(  # type: ignore[func-returns-value]
  |   File "E:\.conda\talking_face\lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
  |     return await self.app(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\fastapi\applications.py", line 1139, in __call__
  |     await super().__call__(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\applications.py", line 112, in __call__
  |     await self.middleware_stack(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\middleware\errors.py", line 187, in __call__
  |     raise exc
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\middleware\errors.py", line 165, in __call__
  |     await self.app(scope, receive, _send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\middleware\exceptions.py", line 62, in __call__
  |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
  |     raise exc
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
  |     await app(scope, receive, sender)
  |   File "E:\.conda\talking_face\lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
  |     await self.app(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\routing.py", line 715, in __call__
  |     await self.middleware_stack(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\routing.py", line 735, in app
  |     await route.handle(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\routing.py", line 288, in handle
  |     await self.app(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\fastapi\routing.py", line 120, in app
  |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
  |     raise exc
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
  |     await app(scope, receive, sender)
  |   File "E:\.conda\talking_face\lib\site-packages\fastapi\routing.py", line 107, in app
  |     await response(scope, receive, send)
  |   File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 268, in __call__
  |     await wrap(partial(self.listen_for_disconnect, receive))
  |   File "E:\.conda\talking_face\lib\site-packages\anyio\_backends\_asyncio.py", line 685, in __aexit__
  |     raise BaseExceptionGroup(
  | exceptiongroup.ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 264, in wrap
    |     await func()
    |   File "E:\.conda\talking_face\lib\site-packages\starlette\responses.py", line 245, in stream_response
    |     async for chunk in self.body_iterator:
    |   File "E:\.conda\talking_face\lib\site-packages\starlette\concurrency.py", line 60, in iterate_in_threadpool
    |     yield await anyio.to_thread.run_sync(_next, as_iterator)
    |   File "E:\.conda\talking_face\lib\site-packages\anyio\to_thread.py", line 56, in run_sync
    |     return await get_async_backend().run_sync_in_worker_thread(
    |   File "E:\.conda\talking_face\lib\site-packages\anyio\_backends\_asyncio.py", line 2364, in run_sync_in_worker_thread
    |     return await future
    |   File "E:\.conda\talking_face\lib\site-packages\anyio\_backends\_asyncio.py", line 864, in run
    |     result = context.run(func, *args)
    |   File "E:\.conda\talking_face\lib\site-packages\starlette\concurrency.py", line 49, in _next
    |     return next(iterator)
    |   File "main.py", line 237, in train_generator
    |     for line in docker_exec_train(
    |   File "E:\projects\talking_face_hw_group1\backend\utils.py", line 70, in docker_exec_train
    |     line = process.stdout.readline()
    | UnicodeDecodeError: 'gbk' codec can't decode byte 0x8f in position 56: illegal multibyte sequence
    +------------------------------------