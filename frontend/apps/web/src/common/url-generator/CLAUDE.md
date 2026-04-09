# URL Generator — Mandatory Pattern for All Routes

## Rule

**All internal URLs and routes in this project MUST be constructed using the `UrlGenerator` class.**

Do NOT:
- Hardcode route strings (e.g. `'/dashboard/'`, `'/login/'`) anywhere outside this folder
- Create a separate `ROUTES` constant object or similar mapping
- Use raw string paths in `<Link href=...>`, `redirect()`, `router.push()`, `revalidatePath()`, or `new URL()`

Do:
- Import and call `UrlGenerator.methodName()` for every route reference
- Add new routes as new static methods on the `UrlGenerator` class
- Add corresponding types in `types.ts` when the route accepts query parameters
- Add parsers in `parsers.ts` when the route uses typed query string params (via `nuqs`)

## How It Works

This pattern uses `nuqs` serializers to build type-safe URLs with optional query parameters:

1. **`parsers.ts`** — Defines `nuqs` parser objects for routes that have query string params. Routes without query params use `emptyParser`.
2. **`types.ts`** — Defines TypeScript types for each route's arguments (path params + query values).
3. **`typed-links.ts`** — The `createTypedLink` helper that combines a route path with a parser to produce a serialized URL string.
4. **`url-generator.ts`** — The `UrlGenerator` class with one static method per route. This is the only public API consumers should import.

## Adding a New Route

1. If the route has query params, add a parser in `parsers.ts` (e.g. `export const myPageParser = { tab: parseAsString };`).
2. Add a type in `types.ts` (e.g. `export type MyPageType = { id: string } & TypedLinkProps<typeof myPageParser>;`).
3. Add a static method in `url-generator.ts`:
   ```ts
   static myPage({ id, options, values }: MyPageType) {
     const route = `/my-page/${id}` as Route;
     return createTypedLink(route, myPageParser, options)(values);
   }
   ```
4. Use it everywhere: `UrlGenerator.myPage({ id: '123' })` or `UrlGenerator.myPage({ id: '123', values: { tab: 'settings' } })`.

## Why

- Single source of truth for every URL in the app
- Type-safe query parameters via `nuqs` serializers
- Refactoring a route path requires changing only one place
- Prevents typos and stale hardcoded strings scattered across the codebase
