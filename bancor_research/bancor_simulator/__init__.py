# coding=utf-8
# --------------------------------------------------------------------------------------------------------------------
# Licensed under the MIT LICENSE. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------------------------------
"""Spec and agent-based simulation modules for Bancor v3."""

import warnings

import bancor_research.bancor_simulator.v3.spec

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    warnings.simplefilter("ignore", DeprecationWarning)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

__version__ = "3.1.0"
