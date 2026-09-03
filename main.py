import discord
from discord.ext import commands
from discord import app_commands
import os
import asyncio
from dotenv import load_dotenv

# =========================================================
# CONFIGURACIÓN
# =========================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# ID del servidor
GUILD_ID = 1542404762886996048

# Canales
WELCOME_CHANNEL_ID = 1542415613400457226
TICKET_CATEGORY_ID = 1542417079272083556
BETATEST_CHANNEL_ID = 1542414611192610887

# Rol de staff
STAFF_ROLE_ID = 1543653455644590081

# Color principal
PURPLE = discord.Color.from_rgb(145, 70, 255)

# =========================================================
# INTENTS
# =========================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    print("======================================")
    print("       REVIIL STUDIOS BOT")
    print("======================================")
    print(f"Bot: {bot.user}")
    print(f"ID: {bot.user.id}")
    print("Estado: REVIIL STUDIOS")
    print("======================================")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name="REVIIL STUDIOS"
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error sincronizando comandos: {e}")


# =========================================================
# BIENVENIDAS
# =========================================================

@bot.event
async def on_member_join(member):

    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    if channel is None:
        return

    embed = discord.Embed(
        title="👋 ¡Bienvenido a REVIIL STUDIOS!",
        description=(
            f"¡Qué bueno tenerte aquí, {member.mention}!\n\n"
            "🎮 **REVIIL STUDIOS**\n"
            "Un espacio dedicado al desarrollo, "
            "betatesting y creación de proyectos.\n\n"
            "📌 Lee las reglas y mantente atento "
            "a nuestras novedades."
        ),
        color=PURPLE
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.set_footer(
        text="REVIIL STUDIOS • Sistema de bienvenida"
    )

    await channel.send(
        content=f"👋 Bienvenido {member.mention}",
        embed=embed
    )


# =========================================================
# BOTÓN DE TICKETS
# =========================================================

class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Crear Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.primary,
        custom_id="reviil_create_ticket"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        category = guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message(
                "❌ La categoría de tickets no existe.",
                ephemeral=True
            )
            return

        # Comprobar si ya tiene ticket
        for channel in guild.text_channels:

            if channel.name == f"ticket-{user.id}":

                await interaction.response.send_message(
                    f"❌ Ya tienes un ticket abierto: {channel.mention}",
                    ephemeral=True
                )

                return

        staff_role = guild.get_role(STAFF_ROLE_ID)

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
        }

        if staff_role:

            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        channel = await guild.create_text_channel(

            name=f"ticket-{user.id}",

            category=category,

            overwrites=overwrites,

            topic=f"Ticket creado por {user}"
        )

        embed = discord.Embed(

            title="🎫 Ticket creado",

            description=(
                f"Hola {user.mention} 👋\n\n"
                "Gracias por contactar con **REVIIL STUDIOS**.\n\n"
                "📌 Explica detalladamente tu problema o "
                "motivo del ticket.\n\n"
                "🕐 Un miembro del equipo te atenderá "
                "lo antes posible."
            ),

            color=PURPLE
        )

        embed.set_footer(
            text="REVIIL STUDIOS • Sistema de Tickets"
        )

        await channel.send(

            content=user.mention,

            embed=embed,

            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"✅ Ticket creado: {channel.mention}",
            ephemeral=True
        )


# =========================================================
# CERRAR TICKET
# =========================================================

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cerrar Ticket",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="reviil_close_ticket"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.channel

        await interaction.response.send_message(
            "🔒 Este ticket será eliminado en **5 segundos**."
        )

        await asyncio.sleep(5)

        await channel.delete(
            reason="Ticket cerrado"
        )


# =========================================================
# COMANDO PANEL DE TICKETS
# =========================================================

@bot.tree.command(
    name="ticket",
    description="Enviar el panel de tickets de REVIIL STUDIOS"
)
@app_commands.checks.has_permissions(administrator=True)
async def ticket(interaction: discord.Interaction):

    embed = discord.Embed(

        title="🎫 Soporte • REVIIL STUDIOS",

        description=(
            "¿Necesitas ayuda?\n\n"
            "Pulsa el botón de abajo para crear un ticket.\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "📌 **Soporte**\n"
            "🐛 **Reportar bugs**\n"
            "💡 **Sugerencias**\n"
            "🤝 **Colaboraciones**\n"
            "🧪 **Betatest**\n"
            "━━━━━━━━━━━━━━━━━━"
        ),

        color=PURPLE
    )

    embed.set_footer(
        text="REVIIL STUDIOS • Soporte"
    )

    await interaction.channel.send(
        embed=embed,
        view=TicketView()
    )

    await interaction.response.send_message(
        "✅ Panel de tickets enviado.",
        ephemeral=True
    )


# =========================================================
# BETATEST
# =========================================================

class BetaTestView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Unirme al BETATEST",
        emoji="🧪",
        style=discord.ButtonStyle.success,
        custom_id="reviil_betatest"
    )
    async def betatest(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        role = discord.utils.get(
            guild.roles,
            name="BETATEST"
        )

        if role is None:

            role = await guild.create_role(
                name="BETATEST",
                color=PURPLE,
                reason="REVIIL STUDIOS BETATEST"
            )

        if role in user.roles:

            await interaction.response.send_message(
                "🧪 Ya formas parte del **BETATEST**.",
                ephemeral=True
            )

            return

        try:

            await user.add_roles(role)

            await interaction.response.send_message(
                "🧪 **¡Bienvenido al BETATEST de REVIIL STUDIOS!**\n\n"
                "Ahora tienes acceso a los canales de pruebas.",
                ephemeral=True
            )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para darte el rol.",
                ephemeral=True
            )


# =========================================================
# PANEL BETATEST
# =========================================================

@bot.tree.command(
    name="betatest",
    description="Enviar el panel de BETATEST"
)
@app_commands.checks.has_permissions(administrator=True)
async def betatest(interaction: discord.Interaction):

    embed = discord.Embed(

        title="🧪 BETATEST SERVER",

        description=(
            "# REVIIL STUDIOS\n\n"

            "🚀 **¿Quieres probar nuestros proyectos antes "
            "que nadie?**\n\n"

            "El servidor **BETATEST** está diseñado para "
            "probar nuestros proyectos antes de su lanzamiento.\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            "🧪 **¿Qué podrás hacer?**\n"
            "• Probar nuevas funciones\n"
            "• Reportar bugs\n"
            "• Dar feedback\n"
            "• Proponer mejoras\n"
            "• Ver novedades antes del lanzamiento\n\n"

            "━━━━━━━━━━━━━━━━━━\n"

            "⚠️ **IMPORTANTE**\n"
            "Las funciones del BETATEST pueden contener errores "
            "o cambios inesperados.\n\n"

            "Pulsa el botón para formar parte del equipo "
            "de testers."
        ),

        color=PURPLE
    )

    embed.set_footer(
        text="REVIIL STUDIOS • BETATEST SERVER"
    )

    await interaction.channel.send(
        embed=embed,
        view=BetaTestView()
    )

    await interaction.response.send_message(
        "✅ Panel de BETATEST enviado.",
        ephemeral=True
    )


# =========================================================
# EMBED GENERATOR
# =========================================================

@bot.tree.command(
    name="embed",
    description="Crear un embed personalizado"
)
@app_commands.describe(
    titulo="Título del embed",
    descripcion="Descripción del embed",
    color="Color HEX, ejemplo: #8B5CF6",
    footer="Texto del footer",
    imagen="URL de una imagen",
    thumbnail="URL del thumbnail"
)
@app_commands.checks.has_permissions(
    manage_messages=True
)
async def embed_generator(

    interaction: discord.Interaction,

    titulo: str,

    descripcion: str,

    color: str = "#9146FF",

    footer: str = "REVIIL STUDIOS",

    imagen: str = "",

    thumbnail: str = ""
):

    try:

        color = color.replace("#", "")

        color_value = int(color, 16)

        embed_color = discord.Color(color_value)

    except:

        await interaction.response.send_message(
            "❌ Color inválido. Usa un formato como `#9146FF`.",
            ephemeral=True
        )

        return

    embed = discord.Embed(

        title=titulo,

        description=descripcion,

        color=embed_color
    )

    if footer:
        embed.set_footer(text=footer)

    if imagen:
        embed.set_image(url=imagen)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    await interaction.channel.send(
        embed=embed
    )

    await interaction.response.send_message(
        "✅ Embed creado correctamente.",
        ephemeral=True
    )


# =========================================================
# COMANDO INFO
# =========================================================

@bot.tree.command(
    name="reviil",
    description="Información de REVIIL STUDIOS"
)
async def reviil(interaction: discord.Interaction):

    embed = discord.Embed(

        title="🟣 REVIIL STUDIOS",

        description=(
            "**REVIIL STUDIOS**\n\n"
            "🎮 Desarrollo de proyectos\n"
            "🧪 Servidores BETATEST\n"
            "💻 Desarrollo y programación\n"
            "🎨 Diseño y creatividad\n\n"
            "🚀 Construyendo nuevos proyectos."
        ),

        color=PURPLE
    )

    embed.set_footer(
        text="REVIIL STUDIOS"
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# ERROR HANDLER
# =========================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error
):

    if isinstance(
        error,
        app_commands.errors.MissingPermissions
    ):

        message = (
            "❌ No tienes permisos suficientes "
            "para utilizar este comando."
        )

    else:

        message = f"❌ Ocurrió un error:\n`{error}`"

    if interaction.response.is_done():

        await interaction.followup.send(
            message,
            ephemeral=True
        )

    else:

        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# =========================================================
# VIEWS PERSISTENTES
# =========================================================

bot.add_view(TicketView())
bot.add_view(CloseTicketView())
bot.add_view(BetaTestView())


# =========================================================
# INICIAR BOT
# =========================================================

if not TOKEN:

    print(
        "❌ ERROR: No se encontró DISCORD_TOKEN "
        "en las variables de entorno."
    )

else:

    bot.run(TOKEN)
