# Copyright (C) 2021 Avery
#
# This file is part of py18n.
#
# py18n is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# py18n is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with py18n.  If not, see <http://www.gnu.org/licenses/>.


import contextvars
from typing import Callable, List, Optional, Union

from discord.ext import commands

try:
    from .i18n import I18n
    from .language import Language
except ImportError:
    from i18n import I18n
    from language import Language

class I18nExtension(I18n):
    default_i18n_instance = None

    def __init__(self, languages: List[Language], fallback: Union[str, int], bot: Optional[commands.Bot] = None, default: bool = True) -> None:
        super().__init__(languages, fallback)
        self._current_locale = contextvars.ContextVar("_current_locale")
        self._bot = None

        if default or I18nExtension.default_i18n_instance is None:
            I18nExtension.default_i18n_instance = self

    def init_bot(self, bot: commands.Bot, get_locale_func: Callable = None):
        """
        Initialize the given bot with the pre-invoke hooks to set the current
        context. 

        .. note ::

            Due to how discord.py works, this will override any previously
            set global pre-invoke hook.

            I recommend creating an override to have multiple pre- and post-
            invoke hooks if required, or setting the current locale yourself
            with :func`set_current_locale`.

        Parameters
        ----------
        bot : commands.Bot
            The bot to attach to
        get_locale_func : Callable, optional
            The function that provides the locale code for the context, by default None

            It should take one argument, of type :cls:`discord.ext.commands.Context`
        """
        self._bot = bot
        if get_locale_func is None:
            get_locale_func = lambda *_: self._fallback

        async def pre(ctx):
            ctx.set_current_locale(get_locale_func(ctx))

        self._bot.before_invoke(pre)

    def set_current_locale(self, locale: str) -> str:
        """
        Set the current locale (for this context)

        Parameters
        ----------
        locale : str
            The locale
        """
        self._current_locale.set(locale)

    def get_current_locale(self) -> str:
        """
        Get the locale for this context, or the fallback locale if none is set

        Returns
        -------
        str
            The locale
        """
        return self._current_locale.get(self._fallback)

    @classmethod
    def contextual_get_text(
        cls,
        key: str,
        list_formatter: bool = None,
        use_translations: bool = True,
        should_fallback: bool = True,
        **kwargs
    ) -> str:
        i18n = cls.default_i18n_instance
        if i18n is None:
            raise NameError("No default i18n instance has been initialized!")

        return i18n.get_text(
            key, i18n.get_current_locale(), list_formatter=list_formatter,
            use_translations=use_translations, should_fallback=should_fallback,
            **kwargs)

_ = I18nExtension.contextual_get_text