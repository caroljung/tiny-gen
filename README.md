

## tiny-gen

A small webapp that takes in a github repo url and a command prompt, and returns a unified git diff 📜
Read https://codegen.notion.site/codegen/TinyGen-fefcb1f1e25048b6a102465c9e69a539 for more details.


This is a hybrid Next.js + Python app that uses Next.js as the frontend and FastAPI as the API backend.

## Demo

https://tiny-gen.vercel.app

https://tiny-gen.vercel.app/apis/generate-diff for direct API


## Run it locally

First, install the dependencies:

```bash
npm install
# or
yarn
# or
pnpm install
```

Run locally by executing
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the UI. Running it locally will help reduce timeouts enforced by Vercel, the free web hosting service. 😿
You can also hit the backend APIS at [http://127.0.0.1:8000](http://127.0.0.1:8000).

You can also test the streaming API by running
```
python test/test_generate_diff.py
```
