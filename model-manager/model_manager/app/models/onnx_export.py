from transformers import AutoModelWithHeads, AutoModel, AutoTokenizer, AutoConfig
from transformers.onnx import OnnxConfig, export

from onnxruntime.quantization import quantize_dynamic, QuantType

from huggingface_hub import HfApi, hf_hub_download
from huggingface_hub.utils import RepositoryNotFoundError

import os

from typing import Mapping, OrderedDict, Optional
from pathlib import Path

import json

from importlib import import_module


# Mappings from HF AutoConfig (prepended Onnx to get AutoOnnxConfig)
CONFIG_MAPPING_NAMES = OrderedDict(
    [
        # Add configs here
        ("albert", "AlbertOnnxConfig"),
        ("audio-spectrogram-transformer", "ASTOnnxConfig"),
        ("bart", "BartOnnxConfig"),
        ("beit", "BeitOnnxConfig"),
        ("bert", "BertOnnxConfig"),
        ("bert-generation", "BertGenerationOnnxConfig"),
        ("big_bird", "BigBirdOnnxConfig"),
        ("bigbird_pegasus", "BigBirdPegasusOnnxConfig"),
        ("blenderbot", "BlenderbotOnnxConfig"),
        ("blenderbot-small", "BlenderbotSmallOnnxConfig"),
        ("bloom", "BloomOnnxConfig"),
        ("camembert", "CamembertOnnxConfig"),
        ("canine", "CanineOnnxConfig"),
        ("chinese_clip", "ChineseCLIPOnnxConfig"),
        ("clip", "CLIPOnnxConfig"),
        ("clipseg", "CLIPSegOnnxConfig"),
        ("codegen", "CodeGenOnnxConfig"),
        ("conditional_detr", "ConditionalDetrOnnxConfig"),
        ("convbert", "ConvBertOnnxConfig"),
        ("convnext", "ConvNextOnnxConfig"),
        ("ctrl", "CTRLOnnxConfig"),
        ("cvt", "CvtOnnxConfig"),
        ("data2vec-audio", "Data2VecAudioOnnxConfig"),
        ("data2vec-text", "Data2VecTextOnnxConfig"),
        ("data2vec-vision", "Data2VecVisionOnnxConfig"),
        ("deberta", "DebertaOnnxConfig"),
        ("deberta-v2", "DebertaV2OnnxConfig"),
        ("decision_transformer", "DecisionTransformerOnnxConfig"),
        ("deformable_detr", "DeformableDetrOnnxConfig"),
        ("deit", "DeiTOnnxConfig"),
        ("detr", "DetrOnnxConfig"),
        ("dinat", "DinatOnnxConfig"),
        ("distilbert", "DistilBertOnnxConfig"),
        ("donut-swin", "DonutSwinOnnxConfig"),
        ("dpr", "DPROnnxConfig"),
        ("dpt", "DPTOnnxConfig"),
        ("electra", "ElectraOnnxConfig"),
        ("encoder-decoder", "EncoderDecoderOnnxConfig"),
        ("ernie", "ErnieOnnxConfig"),
        ("esm", "EsmOnnxConfig"),
        ("flaubert", "FlaubertOnnxConfig"),
        ("flava", "FlavaOnnxConfig"),
        ("fnet", "FNetOnnxConfig"),
        ("fsmt", "FSMTOnnxConfig"),
        ("funnel", "FunnelOnnxConfig"),
        ("glpn", "GLPNOnnxConfig"),
        ("gpt2", "GPT2OnnxConfig"),
        ("gpt_neo", "GPTNeoOnnxConfig"),
        ("gpt_neox", "GPTNeoXOnnxConfig"),
        ("gpt_neox_japanese", "GPTNeoXJapaneseOnnxConfig"),
        ("gptj", "GPTJOnnxConfig"),
        ("groupvit", "GroupViTOnnxConfig"),
        ("hubert", "HubertOnnxConfig"),
        ("ibert", "IBertOnnxConfig"),
        ("imagegpt", "ImageGPTOnnxConfig"),
        ("jukebox", "JukeboxOnnxConfig"),
        ("layoutlm", "LayoutLMOnnxConfig"),
        ("layoutlmv2", "LayoutLMv2OnnxConfig"),
        ("layoutlmv3", "LayoutLMv3OnnxConfig"),
        ("led", "LEDOnnxConfig"),
        ("levit", "LevitOnnxConfig"),
        ("lilt", "LiltOnnxConfig"),
        ("longformer", "LongformerOnnxConfig"),
        ("longt5", "LongT5OnnxConfig"),
        ("luke", "LukeOnnxConfig"),
        ("lxmert", "LxmertOnnxConfig"),
        ("m2m_100", "M2M100OnnxConfig"),
        ("marian", "MarianOnnxConfig"),
        ("markuplm", "MarkupLMOnnxConfig"),
        ("maskformer", "MaskFormerOnnxConfig"),
        ("maskformer-swin", "MaskFormerSwinOnnxConfig"),
        ("mbart", "MBartOnnxConfig"),
        ("mctct", "MCTCTOnnxConfig"),
        ("megatron-bert", "MegatronBertOnnxConfig"),
        ("mobilebert", "MobileBertOnnxConfig"),
        ("mobilenet_v1", "MobileNetV1OnnxConfig"),
        ("mobilenet_v2", "MobileNetV2OnnxConfig"),
        ("mobilevit", "MobileViTOnnxConfig"),
        ("mpnet", "MPNetOnnxConfig"),
        ("mt5", "MT5OnnxConfig"),
        ("mvp", "MvpOnnxConfig"),
        ("nat", "NatOnnxConfig"),
        ("nezha", "NezhaOnnxConfig"),
        ("nystromformer", "NystromformerOnnxConfig"),
        ("openai-gpt", "OpenAIGPTOnnxConfig"),
        ("opt", "OPTOnnxConfig"),
        ("owlvit", "OwlViTOnnxConfig"),
        ("pegasus", "PegasusOnnxConfig"),
        ("pegasus_x", "PegasusXOnnxConfig"),
        ("perceiver", "PerceiverOnnxConfig"),
        ("plbart", "PLBartOnnxConfig"),
        ("poolformer", "PoolFormerOnnxConfig"),
        ("prophetnet", "ProphetNetOnnxConfig"),
        ("qdqbert", "QDQBertOnnxConfig"),
        ("rag", "RagOnnxConfig"),
        ("realm", "RealmOnnxConfig"),
        ("reformer", "ReformerOnnxConfig"),
        ("regnet", "RegNetOnnxConfig"),
        ("rembert", "RemBertOnnxConfig"),
        ("resnet", "ResNetOnnxConfig"),
        ("retribert", "RetriBertOnnxConfig"),
        ("roberta", "RobertaOnnxConfig"),
        ("roc_bert", "RoCBertOnnxConfig"),
        ("roformer", "RoFormerOnnxConfig"),
        ("segformer", "SegformerOnnxConfig"),
        ("sew", "SEWOnnxConfig"),
        ("sew-d", "SEWDOnnxConfig"),
        ("speech-encoder-decoder", "SpeechEncoderDecoderOnnxConfig"),
        ("speech_to_text", "Speech2TextOnnxConfig"),
        ("speech_to_text_2", "Speech2Text2OnnxConfig"),
        ("splinter", "SplinterOnnxConfig"),
        ("squeezebert", "SqueezeBertOnnxConfig"),
        ("swin", "SwinOnnxConfig"),
        ("swinv2", "Swinv2OnnxConfig"),
        ("switch_transformers", "SwitchTransformersOnnxConfig"),
        ("t5", "T5OnnxConfig"),
        ("table-transformer", "TableTransformerOnnxConfig"),
        ("tapas", "TapasOnnxConfig"),
        ("time_series_transformer", "TimeSeriesTransformerOnnxConfig"),
        ("trajectory_transformer", "TrajectoryTransformerOnnxConfig"),
        ("transfo-xl", "TransfoXLOnnxConfig"),
        ("trocr", "TrOCROnnxConfig"),
        ("unispeech", "UniSpeechOnnxConfig"),
        ("unispeech-sat", "UniSpeechSatOnnxConfig"),
        ("van", "VanOnnxConfig"),
        ("videomae", "VideoMAEOnnxConfig"),
        ("vilt", "ViltOnnxConfig"),
        ("vision-encoder-decoder", "VisionEncoderDecoderOnnxConfig"),
        ("vision-text-dual-encoder", "VisionTextDualEncoderOnnxConfig"),
        ("visual_bert", "VisualBertOnnxConfig"),
        ("vit", "ViTOnnxConfig"),
        ("vit_mae", "ViTMAEOnnxConfig"),
        ("vit_msn", "ViTMSNOnnxConfig"),
        ("wav2vec2", "Wav2Vec2OnnxConfig"),
        ("wav2vec2-conformer", "Wav2Vec2ConformerOnnxConfig"),
        ("wavlm", "WavLMOnnxConfig"),
        ("whisper", "WhisperOnnxConfig"),
        ("xclip", "XCLIPOnnxConfig"),
        ("xglm", "XGLMOnnxConfig"),
        ("xlm", "XLMOnnxConfig"),
        ("xlm-prophetnet", "XLMProphetNetOnnxConfig"),
        ("xlm-roberta", "XLMRobertaOnnxConfig"),
        ("xlm-roberta-xl", "XLMRobertaXLOnnxConfig"),
        ("xlnet", "XLNetOnnxConfig"),
        ("yolos", "YolosOnnxConfig"),
        ("yoso", "YosoOnnxConfig"),
    ]
)

def auto_onnx_config(model_name: str, task: str) -> OnnxConfig:
    """
    Returns a HF onnx config for the given model name if it exists
    @ model_name: the name of the model (e.g. facebook/bart-base)
    @ task: the task for which the model is used (e.g. question-answering)
    """
    try:
        config = AutoConfig.from_pretrained(model_name)

        # Assumes that the identifier of model_name "facebook/bart-base" is "bart"
        identifier = model_name.split("/")[-1].split("-")[0]

        config_name = CONFIG_MAPPING_NAMES[identifier]
        config_class = import_module(f"transformers.models.{identifier}")
        auto_onnx_config = getattr(config_class, config_name)
        return auto_onnx_config.from_model_config(config, task=task)
    except:
        raise ValueError(f"Could not find an AutoOnnxConfig for model {model_name}.")


def generate_readme(directory_path: str, base_model: str, skill: str, model_id: str, adapter: Optional[str] = None):
    """
    Generates a README.md file for the exported model
    @ directory_path: the path to the directory where the README.md file will be generated
    @ base_model: the name of the base model (e.g. facebook/bart-base)
    @ skill: the skill for which the model is exported (e.g. question-answering)
    @ model_id: the id of the model (e.g. bart-base-pf-narrativeqa-onnx)
    @ adapter: the adapter used for the export (if model is an adapter model)
    """

    onnx_readme = "{}/README.md".format(directory_path)

    if adapter is None:
        readme_path = hf_hub_download(repo_id=base_model, filename="README.md")

        inserted_headline = False
        with open(readme_path, 'r') as src, open(onnx_readme, 'w') as dst:
            for line in src:
                # Insert onnx tag
                if line == 'tags:\n':
                    dst.write("inference: false\n")
                    dst.write(line)
                    dst.write('- onnx\n')
                    continue

                if line.startswith("# ") and not inserted_headline:
                    inserted_headline = True
                    dst.write("# ONNX export of " + base_model + "\n")
                    continue

                dst.write(line)
    else:
        readme_path = hf_hub_download(repo_id=adapter, filename="README.md")

        skip = False
        with open(readme_path, 'r') as src, open(onnx_readme, 'w') as dst:
            for line in src:
                # Insert onnx tag
                if line == 'tags:\n':
                    dst.write("inference: false\n")
                    dst.write(line)
                    dst.write('- onnx\n')
                    continue

                if line.startswith("# Adapter"):
                    skip = True

                    # Insert custom README
                    dst.write("# ONNX export of " + line[2:])
                    dst.write(f"## Conversion of [{adapter}](https://huggingface.co/{adapter}) for UKP SQuARE\n\n\n")
                    dst.write("## Usage\n")
                    dst.write("```python\n")
                    dst.write(f"onnx_path = hf_hub_download(repo_id='UKP-SQuARE/{model_id}', filename='model.onnx') # or model_quant.onnx for quantization\n")
                    dst.write("onnx_model = InferenceSession(onnx_path, providers=['CPUExecutionProvider'])\n\n")

                    if (skill == "span-extraction"):
                        dst.write("context = 'ONNX is an open format to represent models. The benefits of using ONNX include interoperability of frameworks and hardware optimization.'\n")
                        dst.write("question = 'What are advantages of ONNX?'\n")
                        dst.write(f"tokenizer = AutoTokenizer.from_pretrained('UKP-SQuARE/{model_id}')\n\n")
                        dst.write("inputs = tokenizer(question, context, padding=True, truncation=True, return_tensors='np')\n")
                        dst.write("outputs = onnx_model.run(input_feed=dict(inputs), output_names=None)\n")
                        dst.write("```\n\n")

                    elif (skill == "categorical"):
                        dst.write("context = 'English orthography typically represents vowel sounds with the five conventional vowel letters ⟨a, e, i, o, u⟩, as well as ⟨y⟩, which may also be a consonant depending on context. However, outside of abbreviations, there are a handful of words in English that do not have vowels, either because the vowel sounds are not written with vowel letters or because the words themselves are pronounced without vowel sounds'.\n")
                        dst.write("question = 'can there be a word without a vowel'\n")
                        dst.write(f"tokenizer = AutoTokenizer.from_pretrained('UKP-SQuARE/{model_id}')\n\n")
                        dst.write("inputs = tokenizer(question, context, padding=True, truncation=True, return_tensors='np')\n")
                        dst.write("outputs = onnx_model.run(input_feed=dict(inputs), output_names=None)\n")
                        dst.write("```\n\n")

                    elif skill == "multiple-choice":
                        dst.write("context = 'ONNX is an open format to represent models. The benefits of using ONNX include interoperability of frameworks and hardware optimization.'\n")
                        dst.write("question = 'What are advantages of ONNX?'\n")
                        dst.write('choices = ["Cat", "Horse", "Tiger", "Fish"]')

                        dst.write(f"tokenizer = AutoTokenizer.from_pretrained('UKP-SQuARE/{model_id}')\n\n")

                        dst.write("raw_input = [[context, question + " " + choice] for choice in choices]\n")
                        dst.write('inputs = tokenizer(raw_input, padding=True, truncation=True, return_tensors="np")\n')

                        dst.write("inputs['token_type_ids'] = np.expand_dims(inputs['token_type_ids'], axis=0)\n")
                        dst.write("inputs['input_ids'] =  np.expand_dims(inputs['input_ids'], axis=0)\n")
                        dst.write("inputs['attention_mask'] =  np.expand_dims(inputs['attention_mask'], axis=0)\n")
                        dst.write("outputs = onnx_model.run(input_feed=dict(inputs), output_names=None)\n")

                        dst.write("```\n\n")

                    elif skill == "abstractive":
                        dst.write("context = 'ONNX is an open format to represent models. The benefits of using ONNX include interoperability of frameworks and hardware optimization.'\n")
                        dst.write("question = 'What are advantages of ONNX?'\n")
                        dst.write(f"tokenizer = AutoTokenizer.from_pretrained('UKP-SQuARE/{model_id}')\n\n")
                        dst.write("inputs = tokenizer(question, context, padding=True, truncation=True, return_tensors='np')\n")
                        dst.write("outputs = onnx_model.run(input_feed=dict(inputs), output_names=None)\n")
                        dst.write("```\n\n")


                # Continue with normal model card
                if line.startswith("## Architecture & Training"): 
                    skip = False

                if not skip: 
                    dst.write(line)

def push_to_hub(save_dir:str , repository_id: str, hf_token: str):
    """
    Pushes the model to the HuggingFace Hub
    @param save_dir: The directory where the model is saved
    @param repository_id: The name of the repository
    @param hf_token: HuggingFace API token with write access to UKP-SQuARE repository
    """

    api = HfApi()

    api.create_repo(
        token=hf_token,
        repo_id=f'onnxport/{repository_id}',
        exist_ok=True,
        private=False
    )

    for path, subdirs, files in os.walk(save_dir):
        for name in files:
            local_file_path = os.path.join(path, name)
            _, hub_file_path = os.path.split(local_file_path)
            try:
                api.upload_file(
                    token=hf_token,
                    repo_id=f"onnxport/{repository_id}",
                    #repo_id=f"UKP-SQuARE/{repository_id}", TODO replace repo
                    path_or_fileobj=os.path.join(os.getcwd(), local_file_path),
                    path_in_repo=hub_file_path,
                )
            except KeyError:
                pass
            except NameError:
                pass

def onnx_export(model_name: str, skill: str, hf_token: str, adapter_id: Optional[str], custom_onnx_config: Optional[str], quantize_model: bool=True) -> str:
    """
    Exports a model to ONNX format.
    @param model_name: The name of the model to be exported.
    @param skill: The skill of the model to be exported.
    @param quantize_model: Whether to quantize the model.
    @param adapter_id: The id of the adapter to be used (if the model is from the AdapterHub).
    @param custom_onnx_config: The path to a custom config file (if not specified, we try to infer the config from the model)
    """
    model_slur = model_name.split("/")[-1]
    adapter = ""

    if adapter_id:
        adapter = f"AdapterHub/{model_slur}-pf-{adapter_id}"
        model_id = adapter.split("/")[-1]+"-onnx"
    else:
        model_id = model_slur+"-onnx"

    repo_id = f"onnxport/{model_id}" # TODO replace repo
    hf_api = HfApi()
    try:
        # Return repo_id if repository already exists
        hf_api.model_info(repo_id)
        return repo_id
    except RepositoryNotFoundError:
        pass

    # Load model to export
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    

    if adapter_id:
        model = AutoModelWithHeads.from_pretrained(model_name)
        adapter_name = model.load_adapter(adapter, source="hf")
        model.active_adapters = adapter_name
    else:
        model = AutoModel.from_pretrained(model_name)

    if custom_onnx_config:
        class CustomOnnxConfig(OnnxConfig):
            @property
            def inputs(self) -> Mapping[str, Mapping[int, str]]:
                return OrderedDict({k: {int(k2): v2 for k2, v2 in v.items()} for k, v in json.loads(custom_onnx_config).items()})

        print(onnx_config)
        onnx_config = CustomOnnxConfig(model_name, skill)
    else:
        onnx_config = auto_onnx_config(model_name, skill)
    
    # Generate the local directory in onnx/
    directory_path = Path("onnx/{}".format(model_id))
    directory_path.mkdir(parents=True, exist_ok=True)
    onnx_model_path = Path("{}/model.onnx".format(directory_path))

    # Export ONNX model
    export(tokenizer, model, onnx_config, onnx_config.default_onnx_opset, onnx_model_path)

    # Create config.json of vanilla model
    model.save_pretrained(directory_path)
    os.remove(directory_path / "pytorch_model.bin")

    # Save tokenizer
    tokenizer.save_pretrained(directory_path)

    # Create README.md
    generate_readme(directory_path, model_name, skill, model_id, adapter if adapter_id is not None else None)

    if quantize_model:
        quantized_model_path = "{}/model_quant.onnx".format(directory_path)
        quantize_dynamic(onnx_model_path, quantized_model_path, weight_type=QuantType.QInt8)

    print("Uploading model to hub... (may take a few minutes)")
    push_to_hub(
        save_dir = directory_path,
        repository_id = model_id,
        hf_token = hf_token
    )

    return repo_id