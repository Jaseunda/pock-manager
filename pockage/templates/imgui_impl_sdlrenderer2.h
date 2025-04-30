// dear imgui: Renderer Backend for SDL_Renderer
// (Requires: SDL 2.0.17+)

// Implemented features:
//  [X] Renderer: User texture binding. Use 'SDL_Texture*' as ImTextureID. Read the FAQ about ImTextureID!
//  [X] Renderer: Large meshes support (64k+ vertices) with 16-bit indices.
//  [X] Renderer: Multi-viewport support (multiple windows).

// About SDL_Renderer backend:
// - SDL_Renderer is a little more limited than a fully-featured graphics API:
//   it provides a limited "retained-mode" API, not an "immediate-mode" API.
//   We emulate an immediate-mode API by retaining a fair amount of data and
//   not uploading/updating them until RenderDrawData() is called.
// - For this reason, SDL_Renderer's performances with many draw calls can be
//   lower than another graphics API.

// You can use unmodified imgui_impl_* files in your project. See examples/ folder for examples of using this.
// Prefer including the entire imgui/ repository into your project (either as a copy or as a submodule), and only build the backends you need.
// Learn about Dear ImGui:
// - FAQ                  https://dearimgui.com/faq
// - Getting Started     https://dearimgui.com/getting-started
// - Documentation       https://dearimgui.com/docs (same as your local docs/ folder).
// - Introduction, links and more at the top of imgui.cpp

#pragma once
#include "imgui.h"      // IMGUI_IMPL_API

struct SDL_Renderer;
struct SDL_Texture;

IMGUI_IMPL_API bool     ImGui_ImplSDLRenderer2_Init(SDL_Renderer* renderer);
IMGUI_IMPL_API void     ImGui_ImplSDLRenderer2_Shutdown();
IMGUI_IMPL_API void     ImGui_ImplSDLRenderer2_NewFrame();
IMGUI_IMPL_API void     ImGui_ImplSDLRenderer2_RenderDrawData(ImDrawData* draw_data);

// Called by Init/NewFrame/Shutdown
IMGUI_IMPL_API bool     ImGui_ImplSDLRenderer2_CreateFontsTexture();
IMGUI_IMPL_API void     ImGui_ImplSDLRenderer2_DestroyFontsTexture();
IMGUI_IMPL_API bool     ImGui_ImplSDLRenderer2_CreateDeviceObjects();
IMGUI_IMPL_API void     ImGui_ImplSDLRenderer2_DestroyDeviceObjects();