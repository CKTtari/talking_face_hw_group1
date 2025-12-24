import os, sys
sys.path.append('./')
import argparse
import traceback
import gradio as gr
print(gr.__version__)
from inference.mimictalk_infer import AdaptGeneFace2Infer
from inference.train_mimictalk_on_a_video import LoRATrainer
from utils.commons.hparams import hparams

class Trainer():
    def __init__(self):
        pass
    
    def train_once_args(self, *args, **kargs):
        assert len(kargs) == 0
        args = [
            '', # head_ckpt
            'checkpoints/mimictalk_orig/os_secc2plane_torso/', # torso_ckpt
            args[0], 
            '',
            10000,
            1,
            False,
            0.001,
            0.005,
            0.2,
            'secc2plane_sr',
            2,
        ]
        keys = [
            'head_ckpt',
            'torso_ckpt',
            'video_id',
            'work_dir',
            'max_updates',
            'batch_size',
            'test',
            'lr',
            'lr_triplane',
            'lambda_lpips',
            'lora_mode',
            'lora_r',
        ]
        inp = {}
        info = ""
        
        try:
            for key_index in range(len(keys)):
                key = keys[key_index]
                inp[key] = args[key_index]
                if '_name' in key:
                    inp[key] = inp[key] if inp[key] is not None else ''
            
            if inp['video_id'] == '':
                info = "Input Error: Source video is REQUIRED!"
                raise ValueError 

            inp['out_name'] = ''
            inp['seed'] = 42
            
            if inp['work_dir'] is None or inp['work_dir'] == '':
                video_id = os.path.basename(inp['video_id'])[:-4] if inp['video_id'].endswith((".mp4", ".png", ".jpg", ".jpeg")) else inp['video_id']
                inp['work_dir'] = f'checkpoints_mimictalk/{video_id}'
            try:
                trainer = LoRATrainer(inp)
                trainer.training_loop(inp)
            except Exception as e:
                content = f"{e}"
                info = f"Training ERROR: {content}"
                traceback.print_exc()
                raise ValueError
        except Exception as e:
            if info == "":
                content = f"{e}"
                info = f"WebUI ERROR: {content}"
                traceback.print_exc()

        if len(info) > 0:
            print(info)
            info_gr = gr.update(visible=True, value=info)
        else:
            info_gr = gr.update(visible=False, value=info)

        # 使用 Textbox 替代 FileExplorer
        torso_model_dir = gr.update(value=inp['work_dir'])
            
        return info_gr, torso_model_dir

class Inferer(AdaptGeneFace2Infer):
    def infer_once_args(self, *args, **kargs):
        assert len(kargs) == 0
        keys = [
            'drv_audio_name',
            'drv_pose_name',
            'drv_talking_style_name',
            'bg_image_name',
            'blink_mode',
            'temperature',
            'cfg_scale',
            'out_mode',
            'map_to_init_pose',
            'low_memory_usage',
            'hold_eye_opened',
            'a2m_ckpt',
            'torso_ckpt',
            'min_face_area_percent',
        ]
        inp = {}
        out_name = None
        info = ""
        
        try:
            for key_index in range(len(keys)):
                key = keys[key_index]
                inp[key] = args[key_index]
                if '_name' in key:
                    inp[key] = inp[key] if inp[key] is not None else ''
            
            inp['head_ckpt'] = ''
            
            if inp['drv_audio_name'] == '' and inp['drv_pose_name'] == '':
                info = "Input Error: At least one of driving audio or video is REQUIRED!"
                raise ValueError

            if inp['drv_audio_name'] == '' and inp['drv_pose_name'] != '':
                inp['drv_audio_name'] = inp['drv_pose_name']
                print("No audio input, we use driving pose video for video driving")
                
            if inp['drv_pose_name'] == '':
                inp['drv_pose_name'] = 'static'     
            
            reload_flag = False
            if inp['a2m_ckpt'] != self.audio2secc_dir:
                print("Changes of a2m_ckpt detected, reloading model")
                reload_flag = True
            if inp['head_ckpt'] != self.head_model_dir:
                print("Changes of head_ckpt detected, reloading model")
                reload_flag = True
            if inp['torso_ckpt'] != self.torso_model_dir:
                print("Changes of torso_ckpt detected, reloading model")
                reload_flag = True

            inp['out_name'] = ''
            inp['seed'] = 42
            inp['denoising_steps'] = 20
            print(f"infer inputs : {inp}")
                
            try:
                if reload_flag:
                    self.__init__(inp['a2m_ckpt'], inp['head_ckpt'], inp['torso_ckpt'], inp=inp, device=self.device)
            except Exception as e:
                content = f"{e}"
                info = f"Reload ERROR: {content}"
                traceback.print_exc()
                raise ValueError
            try:
                out_name = self.infer_once(inp)
            except Exception as e:
                content = f"{e}"
                info = f"Inference ERROR: {content}"
                traceback.print_exc()
                raise ValueError
        except Exception as e:
            if info == "":
                content = f"{e}"
                info = f"WebUI ERROR: {content}"
                traceback.print_exc()

        if len(info) > 0:
            print(info)
            info_gr = gr.update(visible=True, value=info)
        else:
            info_gr = gr.update(visible=False, value=info)
        if out_name is not None and len(out_name) > 0 and os.path.exists(out_name):
            print(f"Successfully generated in {out_name}")
            video_gr = gr.update(visible=True, value=out_name)
        else:
            print(out_name)
            print(os.path.exists(out_name))
            print(f"Failed to generate")
            video_gr = gr.update(visible=True, value=out_name)
            
        return video_gr, info_gr

def mimictalk_demo(
    audio2secc_dir,
    head_model_dir,
    torso_model_dir, 
    device='cuda',
    warpfn=None,
    ):

    sep_line = "-" * 40

    infer_obj = Inferer(
        audio2secc_dir=audio2secc_dir, 
        head_model_dir=head_model_dir,
        torso_model_dir=torso_model_dir,
        device=device,
    )
    train_obj = Trainer()

    print(sep_line)
    print("Model loading is finished.")
    print(sep_line)
    with gr.Blocks(analytics_enabled=False) as real3dportrait_interface:
        gr.Markdown("\
            <div align='center'> <h2> MimicTalk: Mimicking a personalized and expressive 3D talking face in minutes (NIPS 2024) </span> </h2> \
            <a style='font-size:18px;color: #a0a0a0' href='https://mimictalk.github.io/'>Homepage</a>  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
        
        sources = None
        with gr.Row():
            with gr.Column(variant='panel'):
                with gr.Tabs(elem_id="source_image"):
                    with gr.TabItem('Upload Training Video'):
                        with gr.Row():
                            src_video_name = gr.Video(label="Source video (required for training)", sources=sources, value=None)
                with gr.Tabs(elem_id="driven_audio"):
                    with gr.TabItem('Upload Driving Audio'):
                        with gr.Column(variant='panel'):
                            drv_audio_name = gr.Audio(label="Input audio (required for inference)", sources=sources, type="filepath", value=None)
                with gr.Tabs(elem_id="driven_style"):
                    with gr.TabItem('Upload Style Prompt'):
                        with gr.Column(variant='panel'):
                            drv_style_name = gr.Video(label="Driven Style (optional for inference)", sources=sources, value=None)
                with gr.Tabs(elem_id="driven_pose"):
                    with gr.TabItem('Upload Driving Pose'):
                        with gr.Column(variant='panel'):
                            drv_pose_name = gr.Video(label="Driven Pose (optional for inference)", sources=sources, value=None)
                with gr.Tabs(elem_id="bg_image"):
                    with gr.TabItem('Upload Background Image'):
                        with gr.Row():
                            bg_image_name = gr.Image(label="Background image (optional for inference)", sources=sources, type="filepath", value=None)

            with gr.Column(variant='panel'): 
                with gr.Tabs(elem_id="checkbox"):
                    with gr.TabItem('General Settings'):
                        with gr.Column(variant='panel'):
                            blink_mode = gr.Radio(['none', 'period'], value='period', label='blink mode', info="whether to blink periodly")
                            min_face_area_percent = gr.Slider(minimum=0.15, maximum=0.5, step=0.01, label="min_face_area_percent", value=0.2, info='The minimum face area percent in the output frame, to prevent bad cases caused by a too small face.')
                            temperature = gr.Slider(minimum=0.0, maximum=1.0, step=0.025, label="temperature", value=0.2, info='audio to secc temperature')
                            cfg_scale = gr.Slider(minimum=1.0, maximum=3.0, step=0.025, label="talking style cfg_scale", value=1.5, info='higher -> encourage the generated motion more coherent to talking style')
                            out_mode = gr.Radio(['final', 'concat_debug'], value='concat_debug', label='output layout', info="final: only final output ; concat_debug: final output concated with internel features")
                            low_memory_usage = gr.Checkbox(label="Low Memory Usage Mode: save memory at the expense of lower inference speed. Useful when running a low audio (minutes-long).", value=False)
                            map_to_init_pose = gr.Checkbox(label="Whether to map pose of first frame to initial pose", value=True)
                            hold_eye_opened = gr.Checkbox(label="Whether to maintain eyes always open")
                         
                            train_submit = gr.Button('Train', elem_id="train", variant='primary')
                            infer_submit = gr.Button('Generate', elem_id="generate", variant='primary')
                        
                    with gr.Tabs(elem_id="genearted_video"):
                        info_box = gr.Textbox(label="Error", interactive=False, visible=False)
                        gen_video = gr.Video(label="Generated video", format="mp4", visible=True)
            with gr.Column(variant='panel'): 
                with gr.Tabs(elem_id="checkbox"):
                    with gr.TabItem('Checkpoints'):
                        with gr.Column(variant='panel'):
                            ckpt_info_box = gr.Textbox(value="Please enter the checkpoint path manually (e.g., checkpoints_mimictalk/German_20s/model_ckpt_steps_10000.ckpt)", interactive=False, visible=True, show_label=False)
                            # 使用 Textbox 替代 FileExplorer 避免 glob() root_dir 错误
                            audio2secc_dir_input = gr.Textbox(value=audio2secc_dir, label='audio2secc model ckpt path or directory', max_lines=1)
                            torso_model_dir_input = gr.Textbox(value=torso_model_dir, label='mimictalk model ckpt path or directory', max_lines=1)

        fn = infer_obj.infer_once_args
        if warpfn:
            fn = warpfn(fn)
        infer_submit.click(
            fn=fn, 
            inputs=[
                drv_audio_name,
                drv_pose_name,
                drv_style_name,
                bg_image_name,
                blink_mode,
                temperature,
                cfg_scale,
                out_mode,
                map_to_init_pose,
                low_memory_usage,
                hold_eye_opened,
                audio2secc_dir_input,
                torso_model_dir_input,
                min_face_area_percent,
            ], 
            outputs=[
                gen_video,
                info_box,
            ],
        )
        
        fn_train = train_obj.train_once_args

        train_submit.click(
            fn=fn_train, 
            inputs=[
                src_video_name,
            ], 
            outputs=[
                info_box,
                torso_model_dir_input,
            ],
        )

    print(sep_line)
    print("Gradio page is constructed.")
    print(sep_line)

    return real3dportrait_interface

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--a2m_ckpt", default='checkpoints/240112_icl_audio2secc_vox2_cmlr') 
    parser.add_argument("--head_ckpt", default='') 
    parser.add_argument("--torso_ckpt", default='checkpoints_mimictalk/German_20s/model_ckpt_steps_10000.ckpt') 
    parser.add_argument("--port", type=int, default=None) 
    parser.add_argument("--server", type=str, default='127.0.0.1')
    parser.add_argument("--share", action='store_true', dest='share', help='share server to Internet')

    args = parser.parse_args()
    demo = mimictalk_demo(
        audio2secc_dir=args.a2m_ckpt,
        head_model_dir=args.head_ckpt,
        torso_model_dir=args.torso_ckpt,
        device='cuda:0',
        warpfn=None,
    )
    demo.queue()
    demo.launch(share=args.share, server_name=args.server, server_port=args.port)