#! /bin/bash

# location of the Dropbox folder
DBDIR="${HOME}/Dropbox"



# Stuff that gets synced

DIRECTORIES=(
    Code
    Documents
    anaconda3
)

FILES=(
    ".bashrc"
)


#query Dropbox: if not up and synced, abort
DBST=$(dropbox status)

if [[ $DBST != 'Up to date' ]]; then
    echo "Abort setup: Dropbox is not up to date"
    echo "Dropbox status returns:"
    dropbox status
    exit 1
else
    echo "An initial setup copies local files to Dropbox"
    echo "Otherwise, local files are overwritten with those from Dropbox"
    echo -n "Is this the initial setup (copy files to Dropbox)? [y/n]: "
    read -n 1 ans
    if [[ $ans == y  ]]; then
        echo ""
        echo "Copy directories"
        for DIR in "${DIRECTORIES[@]}"; do
            echo $DIR
            mv $HOME/$DIR $DBDIR/$DIR
        done
        echo "Copy files"
        for FILE in "${FILES[@]}"; do
            echo $FILE
            mv $HOME/$FILE $DBDIR/$FILE
        done
    elif [[ $ans == n  ]]; then
        echo "Remove empty directories"
        for DIR in "${DIRECTORIES[@]}"; do
            echo $DIR
            rmdir $HOME/$DIR
            if [[ $? != 0 ]]; then
                echo -n "${DIR} is not empty - delete contents? [y/n]:"
                read -n 1 ans
                if [[ $ans == y ]]; then
                    rm -rf $HOME/$DIR
                elif [[ $ans == n ]]; then
                    echo ""
                    echo "Check contents of ${DIR} and then rerun this script"
                else
                    echo ""
                    echo "Unrecognized selection - aborting"
                    exit 3
                fi
            fi
        done
        echo "Remove local files"
        for FILE in "${FILES[@]}"; do
            echo $FILE
            rm -f $HOME/$FILE
        done
    else
        echo ""
        echo "Unrecognized selection - aborting"
        exit 2
    fi
    echo ""
    echo "Make symbolic links"
    for DIR in "${DIRECTORIES[@]}"; do
        echo $DIR
        ln -sfn $DBDIR/$DIR $HOME/$DIR
    done
    for FILE in "${FILES[@]}"; do
        echo $FILE
        ln -sfn $DBDIR/$FILE $HOME/$FILE
    done
fi
