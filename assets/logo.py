"""
Módulo para armazenar imagens e ícones em formato base64 ou SVG para uso no streamlit
"""

# Logo principal da guild We Profit como imagem base64
with open("logo_base64.txt", "r") as logo_file:
    logo_base64 = logo_file.read()

# Logo principal da guild We Profit como tag de imagem HTML
LOGO_SVG = f"""
<img src="data:image/jpeg;base64,{logo_base64}" class="guild-logo" alt="We Profit Logo" style="max-width: 200px; filter: drop-shadow(0px 0px 10px rgba(245, 184, 65, 0.5));">
"""

# Ícone simples da guild (só o machado)
ICON_SVG = """
<svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Escudo com borda dourada -->
  <g filter="url(#icon_glow)">
    <path d="M30 5L50 25L40 45L30 55L20 45L10 25L30 5Z" fill="#1A1A1A"/>
    <path d="M30 10L45 27L36 44L30 50L24 44L15 27L30 10Z" stroke="#F5B841" stroke-width="2"/>
  </g>
  
  <!-- Machado de guerra simplificado -->
  <path d="M25 20L30 38L35 20H38L30 45L22 20H25Z" fill="#F5B841"/>
  
  <!-- Efeito de brilho dourado -->
  <defs>
    <filter id="icon_glow" x="0" y="0" width="60" height="60" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
      <feFlood flood-opacity="0" result="BackgroundImageFix"/>
      <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
      <feOffset/>
      <feGaussianBlur stdDeviation="3"/>
      <feComposite in2="hardAlpha" operator="out"/>
      <feColorMatrix type="matrix" values="0 0 0 0 0.961 0 0 0 0 0.722 0 0 0 0 0.255 0 0 0 0.7 0"/>
      <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow"/>
      <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow" result="shape"/>
    </filter>
  </defs>
</svg>
"""