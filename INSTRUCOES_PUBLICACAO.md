# 🌸 SOUL PAPELARIA PERSONALIZADA - Catálogo Digital & Painel

Este projeto contém o catálogo digital interativo completo e painel administrativo da **SOUL PAPELARIA PERSONALIZADA**.

## 🎨 Identidade Visual & Recursos
- **Cores Oficiais:** Bordô Nobre (`#6B1724`), Off-white Suave (`#FAF7F2`) e Dourado Champanhe (`#C5A059`).
- **Tema de Natal:** Efeito de neve caindo na tela (canvas interativo com botão liga/desliga), luzinhas festivas e selos especiais.
- **Categorias Dinâmicas:** Especial de Natal, Papelaria Criativa, Planners, Lembrancinhas e criação ilimitada de novas categorias.
- **Carrinho & WhatsApp:** O cliente monta a seleção de pedidos e envia tudo formatado direto no seu WhatsApp com 1 clique.
- **Painel Administrativo:** Cadastro/remoção de produtos com foto, preço, descrição, gestão de categorias e número do WhatsApp.

---

## 🔐 Acesso ao Painel Administrativo
- **Endereço:** `/admin`
- **Usuário:** `admin`
- **Senha:** `soul123`
*(Você pode alterar a senha no arquivo `server.py` se desejar)*

---

## 🌐 Como colocar o link na Internet 100% Grátis (Para funcionar em qualquer celular e PC)

Para que qualquer cliente abra pelo celular e você gerencie de outro computador mesmo quando o seu PC estiver desligado, o site precisa rodar em um servidor na nuvem gratuito.

### Opção Recomendada: Render.com (100% Grátis)
1. Crie uma conta gratuita em [render.com](https://render.com).
2. Clique em **New +** > **Web Service**.
3. Conecte sua pasta ou repositório do projeto.
4. Configure:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Clique em **Deploy**.
6. Em 2 minutos você terá um link público permanente (ex: `https://soul-papelaria.onrender.com`) pronto para colocar na bio do Instagram e mandar pelo WhatsApp!

