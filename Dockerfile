FROM universalrobots/ursim_e-series:5.15

RUN apt-get update

RUN apt-get install -y openssh-server

# Create sshd runtime directory
RUN mkdir -p /run/sshd

# Enable root login in SSH config
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Enable password authentication
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Expose SSH port
EXPOSE 22

RUN printf '#!/bin/bash\nmkdir -p /run/sshd && chmod 0755 /run/sshd\n/usr/sbin/sshd -D &\nexec /entrypoint.sh "$@"' > /new_entrypoint.sh && \
    chmod a+x /new_entrypoint.sh

RUN echo "root:easybot" | chpasswd

ENTRYPOINT ["/new_entrypoint.sh"]