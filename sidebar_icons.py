"""
Sidebar icons for the Nigerian Payroll System
"""

# Icon SVGs (uses Font Awesome SVG paths)
icons = {
    "dashboard": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M4 13h6a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1zm-1 7a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v4zm10 0a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1v-7a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v7zm1-10h6a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1z"/>
    </svg>
    """,
    
    "calculator": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M4 2h16a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm0 2v4h16V4H4zm0 6v8h7v-8H4zm9 0v8h7v-8h-7zm-6 2h4v1H7v-1zm0 3h4v1H7v-1z"/>
    </svg>
    """,
    
    "employee": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-2a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm9 11a1 1 0 0 1-2 0v-2a3 3 0 0 0-3-3H8a3 3 0 0 0-3 3v2a1 1 0 0 1-2 0v-2a5 5 0 0 1 5-5h8a5 5 0 0 1 5 5v2z"/>
    </svg>
    """,
    
    "employee_detail": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M15 4H5v16h14V8h-4V4zM3 2.992C3 2.444 3.447 2 3.999 2H16l5 5v13.993A1 1 0 0 1 20.007 22H3.993A1 1 0 0 1 3 21.008V2.992zM11 11h2v2h-2v-2zm0 4h2v2h-2v-2z"/>
    </svg>
    """,
    
    "payroll": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm1-11v2h1a3 3 0 0 1 0 6h-1v1h-2v-1H8v-2h4v-2h-1a3 3 0 0 1 0-6h1V8h2v1h3v2h-4z"/>
    </svg>
    """,
    
    "upload": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M8 17a1 1 0 0 1 1-1h6a1 1 0 0 1 0 2H9a1 1 0 0 1-1-1zm9 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM8 12a1 1 0 1 1-2 0 1 1 0 0 1 2 0zm9 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2zm0-5a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM8 7a1 1 0 1 1 0 2 1 1 0 0 1 0-2zM4.5 16.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm0-9a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM12 2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1h2zm0 14a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h2zm9.5-2.5a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3zm0-9a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3z"/>
    </svg>
    """,
    
    "settings": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M9 4.58V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v.58a8 8 0 0 1 1.92 1.11l.5-.29a1 1 0 0 1 1.36.36l2 3.46a1 1 0 0 1-.36 1.36l-.5.29a8.1 8.1 0 0 1 0 2.22l.5.3a1 1 0 0 1 .36 1.35l-2 3.47a1 1 0 0 1-1.36.36l-.5-.3A8 8 0 0 1 15 19.43V20a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-.58a8 8 0 0 1-1.92-1.11l-.5.29a1 1 0 0 1-1.36-.36l-2-3.46a1 1 0 0 1 .36-1.36l.5-.29a8.1 8.1 0 0 1 0-2.22l-.5-.3a1 1 0 0 1-.36-1.35l2-3.47a1 1 0 0 1 1.36-.36l.5.3A8 8 0 0 1 9 4.57zM12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>
    </svg>
    """,
    
    "download": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M4 14a1 1 0 0 1 .93.63l2.12 4.25A3.5 3.5 0 0 0 10.5 21h3a3.5 3.5 0 0 0 3.45-2.12l2.12-4.25a1 1 0 0 1 .93-.63h2a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h2zm9.18-9.94a1 1 0 0 1-.18 1.4L10.4 8.3a2 2 0 0 1-2.8 0L5 5.46a1 1 0 0 1 1.4-1.42L9 6.59V1a1 1 0 0 1 2 0v5.59l2.6-2.55a1 1 0 0 1 1.4.02z"/>
    </svg>
    """,
    
    "success": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm-1-8.41l-3.3-3.3a1 1 0 0 0-1.4 1.42l4 4a1 1 0 0 0 1.4 0l8-8a1 1 0 1 0-1.4-1.42L11 13.59z"/>
    </svg>
    """,
    
    "error": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm-1-5h2v2h-2v-2zm0-8h2v6h-2V7z"/>
    </svg>
    """,
    
    "warning": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 2a9.9 9.9 0 0 1 7.071 2.929A9.9 9.9 0 0 1 22 12a9.9 9.9 0 0 1-2.929 7.071A9.9 9.9 0 0 1 12 22a9.9 9.9 0 0 1-7.071-2.929A9.9 9.9 0 0 1 2 12a9.9 9.9 0 0 1 2.929-7.071A9.9 9.9 0 0 1 12 2zm0 2a8 8 0 1 0 0 16 8 8 0 0 0 0-16zm-.5 5a.5.5 0 0 1 .5.5v5a.5.5 0 0 1-1 0v-5a.5.5 0 0 1 .5-.5zm0 8a.5.5 0 1 1 0 1 .5.5 0 0 1 0-1z"/>
    </svg>
    """,
    
    "info": """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
        <path d="M12 22a10 10 0 1 1 0-20 10 10 0 0 1 0 20zm0-2a8 8 0 1 0 0-16 8 8 0 0 0 0 16zm0-9a1 1 0 0 1 1 1v4a1 1 0 0 1-2 0v-4a1 1 0 0 1 1-1zm0-4a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
    </svg>
    """,
}

def get_icon_html(icon_name, color=None):
    """
    Get the HTML for an icon with optional color styling.
    
    Args:
        icon_name (str): Name of the icon to retrieve
        color (str, optional): CSS color value
    
    Returns:
        str: HTML string for the icon
    """
    icon_svg = icons.get(icon_name, icons["info"])  # Default to info icon if not found
    
    if color:
        icon_svg = icon_svg.replace('fill="currentColor"', f'fill="{color}"')
    
    return f'<span class="icon">{icon_svg}</span>'