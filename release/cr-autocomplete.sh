_cr_complete()
{
    local cur prev

    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}

    case ${COMP_CWORD} in
        1)
            COMPREPLY=($(compgen -W "configure feature move review share update" ${cur}))
            ;;
        2)
            case ${prev} in
                move)
                    branches=$(git for-each-ref --format='%(refname:short)' refs/heads/ 2> /dev/null)
                    if [ $? = 0 ]; then
                        COMPREPLY=($(compgen -W "$(echo $branches)" ${cur}))
                    else
                        COMPREPLY=()
                    fi
                    ;;
            esac
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -F _cr_complete cr