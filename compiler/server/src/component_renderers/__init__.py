"""
Component renderers package.
Auto-imports all component renderer classes.
"""
from .base_renderer import BaseComponentRenderer
from .list_renderer import ListRenderer
from .table_renderer import TableRenderer
from .icon_renderer import IconRenderer
from .gradient_text_renderer import GradientTextRenderer
from .accordion_renderer import AccordionRenderer
from .blur_text_renderer import BlurTextRenderer
from .gradual_blur_renderer import GradualBlurRenderer
from .ribbons_renderer import RibbonsRenderer
from .color_bends_renderer import ColorBendsRenderer
from .plasma_renderer import PlasmaRenderer
from .squares_renderer import SquaresRenderer
from .dark_veil_renderer import DarkVeilRenderer
from .profile_card_renderer import ProfileCardRenderer
from .stepper_renderer import StepperRenderer
from .card_swap_renderer import CardSwapRenderer
from .card_nav_renderer import CardNavRenderer
from .magic_bento_renderer import MagicBentoRenderer


# Registry of all component renderers
COMPONENT_RENDERERS = [
    ListRenderer(),
    TableRenderer(),
    IconRenderer(),
    GradientTextRenderer(),
    AccordionRenderer(),
    BlurTextRenderer(),
    GradualBlurRenderer(),
    RibbonsRenderer(),
    ColorBendsRenderer(),
    PlasmaRenderer(),
    SquaresRenderer(),
    DarkVeilRenderer(),
    ProfileCardRenderer(),
    StepperRenderer(),
    CardSwapRenderer(),
    CardNavRenderer(),
    MagicBentoRenderer(),
]


def get_renderer_for_component(component_type):
    """
    Get the appropriate renderer for a given component type.
    
    Args:
        component_type: The component type (e.g., 'List', 'Table')
        
    Returns:
        BaseComponentRenderer instance or None if no renderer found
    """
    for renderer in COMPONENT_RENDERERS:
        if renderer.can_render(component_type):
            return renderer
    return None


__all__ = [
    'BaseComponentRenderer',
    'COMPONENT_RENDERERS',
    'get_renderer_for_component',
    'ListRenderer',
    'TableRenderer',
    'IconRenderer',
    'GradientTextRenderer',
    'AccordionRenderer',
    'BlurTextRenderer',
    'GradualBlurRenderer',
    'RibbonsRenderer',
    'ColorBendsRenderer',
    'PlasmaRenderer',
    'SquaresRenderer',
    'DarkVeilRenderer',
    'ProfileCardRenderer',
    'StepperRenderer',
    'CardSwapRenderer',
    'CardNavRenderer',
    'MagicBentoRenderer',
]
