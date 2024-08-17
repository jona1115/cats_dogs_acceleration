# Show Branch Name in Bash/Shell Prompt

1. Open your .bashrc file and at the end of it add the following content:  
  ```
  git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
  }

  export PS1="\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] \[\033[00;32m\]\$(git_branch)\[\033[00m\]\$ "
  ```
2. Save and close it. To see the update, please open a new shell or source your current one: `source ~/.bashrc`
