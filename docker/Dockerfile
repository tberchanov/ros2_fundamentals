FROM ros:jazzy

# Basic build tooling + rosdep. Kept in its own layer (separate from the
# sudo install below) so unrelated later changes don't bust this cache and
# force re-downloading these larger packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-colcon-common-extensions \
        python3-rosdep \
        python3-vcstool \
        build-essential \
        git \
        ros-jazzy-rqt-graph \
        ros-jazzy-ros-gz \
    && rm -rf /var/lib/apt/lists/*

RUN if [ ! -d /etc/ros/rosdep/sources.list.d ] || [ -z "$(ls -A /etc/ros/rosdep/sources.list.d 2>/dev/null)" ]; then \
        rosdep init; \
    fi

# Separate apt-get update (rather than reusing the cache from above) since
# the index from an earlier layer shouldn't be trusted for a later install.
RUN apt-get update && apt-get install -y --no-install-recommends sudo \
    && rm -rf /var/lib/apt/lists/*

# Match container user to host user so bind-mounted build artifacts
# (build/, install/, log/) aren't owned by root on the host. The base
# image may already have a user/group at this UID/GID, so reuse it
# (renaming to USERNAME) instead of assuming a clean slate.
ARG UID=1000
ARG GID=1000
ARG USERNAME=devuser
RUN if getent group ${GID} > /dev/null; then \
        groupmod -n ${USERNAME} $(getent group ${GID} | cut -d: -f1); \
    else \
        groupadd -g ${GID} ${USERNAME}; \
    fi \
    && if getent passwd ${UID} > /dev/null; then \
        usermod -l ${USERNAME} -d /home/${USERNAME} -m -g ${GID} $(getent passwd ${UID} | cut -d: -f1); \
    else \
        useradd -m -u ${UID} -g ${GID} -s /bin/bash ${USERNAME}; \
    fi \
    && echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Host GID for the `render` group (see docker-compose.yml's `group_add` /dev/dri
# passthrough for Gazebo's GPU-accelerated GUI). `video`'s GID (44) is already a
# named group in the base image; `render` isn't, which left it as an unresolvable
# numeric GID in the container and made every login shell print
# "groups: cannot find name for group ID <n>" (harmless, but noisy). Naming it
# here makes that go away. Check `getent group render` on the host if this image
# is ever built on different hardware.
ARG RENDER_GID=110
RUN if ! getent group ${RENDER_GID} > /dev/null; then \
        groupadd -g ${RENDER_GID} render; \
    fi \
    && usermod -aG ${RENDER_GID} ${USERNAME}

# Pre-create with correct ownership so the named volume mounted over this
# path (see docker-compose.yml) inherits it on first use, instead of being
# created root-owned.
RUN mkdir -p /home/${USERNAME}/.vscode-server \
    && chown ${UID}:${GID} /home/${USERNAME}/.vscode-server

USER ${USERNAME}
RUN rosdep update

WORKDIR /ros2_ws

COPY --chown=${UID}:${GID} entrypoint.sh /entrypoint.sh
COPY --chown=${UID}:${GID} utils.sh /opt/utils.sh
USER root
RUN chmod +x /entrypoint.sh
USER ${USERNAME}

# Load custom aliases/helpers (docker/utils.sh) in every interactive shell.
RUN echo "source /opt/utils.sh" >> /home/${USERNAME}/.bashrc

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
