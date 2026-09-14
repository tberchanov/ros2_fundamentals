# Shell aliases and helpers for ROS2 workspace work.
# Loaded automatically via ~/.bashrc in every interactive shell.
#
# `docker compose exec ros2 bash` opens a fresh shell that never runs
# entrypoint.sh, so the ROS environment has to be sourced here too.
source /opt/ros/jazzy/setup.bash
if [ -f /ros2_ws/install/setup.bash ]; then
    source /ros2_ws/install/setup.bash
fi

# Always builds against /ros2_ws regardless of the shell's cwd, so running
# `build` from inside src/ (or anywhere else) can't create a stray, separate
# build/install/log tree.
build() {
    echo "Building ROS2 workspace..."
    cd /ros2_ws
    colcon build --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    source /ros2_ws/install/setup.bash

    # Symlink each package's compile_commands.json next to its source so
    # clangd (which looks near the file being edited) can find it.
    for build_dir in build/*/; do
        pkg=$(basename "$build_dir")
        cc="$build_dir/compile_commands.json"
        [ -f "$cc" ] || continue
        pkg_src=$(colcon list --packages-select "$pkg" --paths-only 2>/dev/null)
        [ -n "$pkg_src" ] || continue
        ln -sf "$(realpath --relative-to="$pkg_src" "$cc")" "$pkg_src/compile_commands.json"
    done
}
alias rpl='ros2 pkg list'
