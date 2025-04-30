#include "game.hpp"
#include <SDL2/SDL.h>
#include <iostream>

Game::Game(const std::string& title) : title(title), running(true) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cerr << "SDL could not initialize! SDL_Error: " << SDL_GetError() << std::endl;
        running = false;
    }
}

void Game::run() {
    while (running) {
        update();
        render();
    }
}

void Game::update() {
    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            running = false;
        }
    }
}

void Game::render() {
    // TODO: Implement rendering
}

int main(int argc, char* argv[]) {
    Game game("Pockage Example");
    game.run();
    return 0;
} 