
alias lvi='vim $(find . -maxdepth 1 -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -d" " -f2- )'
alias lcd='cd "$(find . -maxdepth 1 -type d -printf "%T@ %p\n" | sort -n | tail -1 | cut -d" " -f2- )"'
alias ssa='function _ssa() { svn status -u "$1"                 ; }; _ssa'
alias sss='function _sss() { svn status -u "$1" | grep -v "^\?" ; }; _sss'


