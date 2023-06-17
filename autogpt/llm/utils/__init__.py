from __future__ import annotations

from typing import Literal, Optional

from colorama import Fore

from autogpt.config import Config

from ...models.chat_completion_response import ChatCompletionResponse
from ...models.command_function import CommandFunction
from ..api_manager import ApiManager
from ..base import ChatSequence
from ..providers import openai as iopenai
from ..providers.openai import OPEN_AI_CHAT_MODELS
from .token_counter import *


def call_ai_function(
    function: str,
    args: list,
    description: str,
    model: Optional[str] = None,
    config: Optional[Config] = None,
) -> str:
    """Call an AI function

    This is a magic function that can do anything with no-code. See
    https://github.com/Torantulino/AI-Functions for more info.

    Args:
        function (str): The function to call
        args (list): The arguments to pass to the function
        description (str): The description of the function
        model (str, optional): The model to use. Defaults to None.

    Returns:
        str: The response from the function
    """
    if model is None:
        model = config.smart_llm_model
    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]
    # parse args to comma separated string
    arg_str: str = ", ".join(args)

    prompt = ChatSequence.for_model(
        model,
        [
            Message(
                "system",
                f"You are now the following python function: ```# {description}"
                f"\n{function}```\n\nOnly respond with your `return` value.",
            ),
            Message("user", arg_str),
        ],
    )
    return create_chat_completion(prompt=prompt, temperature=0)


def create_text_completion(
    prompt: str,
    model: Optional[str],
    temperature: Optional[float],
    max_output_tokens: Optional[int],
) -> str:
    cfg = Config()
    if model is None:
        model = cfg.fast_llm_model
    if temperature is None:
        temperature = cfg.temperature

    if cfg.use_azure:
        kwargs = {"deployment_id": cfg.get_azure_deployment_id_for_model(model)}
    else:
        kwargs = {"model": model}

    response = iopenai.create_text_completion(
        prompt=prompt,
        **kwargs,
        temperature=temperature,
        max_tokens=max_output_tokens,
        api_key=cfg.openai_api_key,
    )
    logger.debug(f"Response: {response}")

    return response.choices[0].text


# Overly simple abstraction until we create something better
def create_chat_completion(
    prompt: ChatSequence,
    functions: Optional[list[CommandFunction]] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> ChatCompletionResponse:
    """Create a chat completion using the OpenAI API

    Args:
        prompt (ChatSequence): The messages to send to the chat completion
        functions (list[CommandFunction]): The callable functions to be passed to the AI
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.

    Returns:
        str: The response from the chat completion
    """
    cfg = Config()
    functions = functions or []
    if model is None:
        model = prompt.model.name
    if temperature is None:
        temperature = cfg.temperature
    if max_tokens is None:
        max_tokens = OPEN_AI_CHAT_MODELS[model].max_tokens - prompt.token_length

    logger.debug(
        f"{Fore.GREEN}Creating chat completion with model {model}, temperature {temperature}, max_tokens {max_tokens}{Fore.RESET}"
    )
    chat_completion_kwargs = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for plugin in cfg.plugins:
        if plugin.can_handle_chat_completion(
            messages=prompt.raw(),
            **chat_completion_kwargs,
        ):
            message = plugin.handle_chat_completion(
                messages=prompt.raw(),
                **chat_completion_kwargs,
            )
            if message is not None:
                return message

    chat_completion_kwargs["api_key"] = cfg.openai_api_key
    if cfg.use_azure:
        chat_completion_kwargs["deployment_id"] = cfg.get_azure_deployment_id_for_model(
            model
        )

    if functions:
        chat_completion_kwargs["functions"] = [
            function.__dict__ for function in functions
        ]

    response = iopenai.create_chat_completion(
        messages=prompt.raw(),
        **chat_completion_kwargs,
    )
    logger.debug(f"Response: {response}")

    resp = ""
    if not hasattr(response, "error"):
        resp = response.choices[0].message["content"]
    else:
        logger.error(response.error)
        raise RuntimeError(response.error)

    if hasattr(response, "error"):
        logger.error(response.error)
        raise RuntimeError(response.error)

    first_message = response.choices[0].message
    content = first_message["content"]
    function_call = first_message.get("function_call", {})

    for plugin in cfg.plugins:
        if not plugin.can_handle_on_response():
            continue
        content = plugin.on_response(content)

    return ChatCompletionResponse(content=content, function_call=function_call)


def check_model(
    model_name: str, model_type: Literal["smart_llm_model", "fast_llm_model"]
) -> str:
    """Check if model is available for use. If not, return gpt-3.5-turbo-16k-0613."""
    api_manager = ApiManager()
    models = api_manager.get_models()

    if any(model_name in m["id"] for m in models):
        return model_name

    logger.typewriter_log(
        "WARNING: ",
        Fore.YELLOW,
        f"You do not have access to {model_name}. Setting {model_type} to "
        f"gpt-3.5-turbo-16k-0613.",
    )
    return "gpt-3.5-turbo-16k-0613"
