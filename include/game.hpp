#pragma once

#include <string>

class Game {
public:
    Game(const std::string& title);
    void run();
    void update();
    void render();

private:
    std::string title;
    bool running;
}; 