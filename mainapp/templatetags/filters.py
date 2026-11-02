from django import template
register = template.Library()
@register.filter(name='saludo')
def saludo(value):
    salida=f"""
    <div class="flex items-center justify-center min-h-[400px] mt-10">
    <div class="max-w-md w-full bg-gray-800 rounded-2xl shadow-2xl border border-blue-500 transform hover:scale-105 transition-transform duration-300">
        <div class="h-3 bg-blue-500 rounded-t-2xl"></div>

        <div class="p-8 text-center">
            <div class="mx-auto w-24 h-24 rounded-full bg-gray-700 border-4 border-blue-400 flex items-center justify-center mb-6 shadow-inner">
                <span class="text-5xl">👋</span>
            </div>

            <h1 class="text-3xl font-extrabold text-white mb-2 tracking-tight">
                ¡Hola, <span class="text-blue-400">{value}</span>!
            </h1>

            <p class="text-gray-300 text-lg mb-8 leading-relaxed">
                Bienvenido a <span class="font-bold text-yellow-300">Django Site</span>. 
                Estamos listos para tus prácticas  <span class="font-semibold text-blue-300">TICS</span>.
            </p>

           
        </div>
    </div>
</div>
    """
    largo=""
    if len(value)>=20:
        largo=f"<p>tu nombre es muy largo</p>"
    return salida+ largo