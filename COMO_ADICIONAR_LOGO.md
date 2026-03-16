# Como Adicionar a Logo Real da NewC Sport

## Situação Atual
A tela de login está usando um componente de texto estilizado para representar a logo da NewC Sport:
- "New" em azul
- "C" em laranja
- "SPORT" em cinza

## Para Usar uma Imagem Real da Logo

### Opção 1: Arquivo de Imagem Local

1. **Coloque o arquivo da logo** em uma destas pastas:
   ```
   frontend/public/logo-newc.png
   ```
   ou
   ```
   frontend/public/assets/logo-newc.png
   ```

2. **Edite o arquivo** `frontend/src/pages/Login.tsx`

3. **Substitua o componente `NewCSportLogo`** por:
   ```tsx
   // Se a logo estiver em public/logo-newc.png
   <img 
     src="/logo-newc.png" 
     alt="NewC Sport Logo" 
     className="h-20 mx-auto"
   />
   
   // OU se estiver em public/assets/logo-newc.png
   <img 
     src="/assets/logo-newc.png" 
     alt="NewC Sport Logo" 
     className="h-20 mx-auto"
   />
   ```

4. **Ajuste o tamanho** conforme necessário:
   - `h-16` = 64px de altura
   - `h-20` = 80px de altura
   - `h-24` = 96px de altura
   - `h-32` = 128px de altura

### Opção 2: URL Externa

Se a logo estiver hospedada online:

```tsx
<img 
  src="https://exemplo.com/logo-newc.png" 
  alt="NewC Sport Logo" 
  className="h-20 mx-auto"
/>
```

### Opção 3: SVG Inline (Melhor Qualidade)

Se tiver o código SVG da logo:

```tsx
const NewCSportLogo: React.FC = () => {
  return (
    <svg className="h-20 mx-auto" viewBox="0 0 200 100">
      {/* Cole o conteúdo SVG aqui */}
    </svg>
  );
};
```

## Formatos de Imagem Recomendados

- **PNG** com fundo transparente (preferível)
- **SVG** para melhor qualidade em qualquer tamanho
- **JPG** se não precisar de transparência

## Localização no Código

Arquivo: `frontend/src/pages/Login.tsx`
Linhas: 10-23 (componente NewCSportLogo)
Linha 71: Onde o componente é usado

## Exemplo Completo

```tsx
// Remova ou comente o componente NewCSportLogo (linhas 10-23)

// Na linha 71, substitua:
<NewCSportLogo />

// Por:
<img 
  src="/logo-newc.png" 
  alt="NewC Sport" 
  className="h-20 mx-auto object-contain"
/>
```

## Teste

Após fazer a alteração:
1. O Vite recarregará automaticamente
2. Acesse http://localhost:3000
3. Faça logout para ver a tela de login
4. A logo deve aparecer no lugar do texto estilizado



