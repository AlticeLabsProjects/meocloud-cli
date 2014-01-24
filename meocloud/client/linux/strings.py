# -*- coding: utf-8 -*-

NOTIFICATIONS = {
    'en': {
        '200_title': 'File Added',
        '200_description': 'File "{0}" was added to your MEO Cloud folder',
        '201_title': 'File Removed',
        '201_description': 'File "{0}" was removed from your MEO Cloud folder',
        '202_title': 'File Updated',
        '202_description': 'File "{0}" was updated in your MEO Cloud folder',
        '203_title': 'Files Added',
        '203_description': '{0} files were added to your MEO Cloud folder',
        '204_title': 'Files Removed',
        '204_description': '{0} files were removed from your MEO Cloud folder',
        '205_title': 'Files Updated',
        '205_description': '{0} files were updated in your MEO Cloud folder',
        '206_title': 'Files Synchronized',
        '206_description': '{0} files were synchronized in your MEO Cloud folder',
        '207_title': 'Connecting to MEO Cloud...',
        '207_description': 'Please check your Internet connection and proxy settings.',

        '250_title': 'Shared Folder Created',
        '250_description': 'Shared folder "{0}" was created in your MEO Cloud folder',
        '251_title': 'Shared Folder Deleted',
        '251_description': 'Shared folder "{0}" was deleted from your MEO Cloud folder',
        '252_title': 'Shared Folder Unshared',
        '252_description': 'Stopped sharing folder "{0}"',

        '500_title': 'Quota Exceeded',
        '500_description': 'You have exceeded your MEO Cloud quota. Please free more space to continue uploading.',
        '501_title': 'Could not synchronize "{0}"',
        '501_description': 'Could not synchronize "{0}". Please verify that you have sufficient permissions and that the file is not in use.',
        '502_title': 'Insufficient disk space',
        '502_description': 'Could not update "{0}". Please ensure that you have sufficient free disk space.',
        '503_title': 'File "{0}" is in use',
        '503_description': 'File "{0}" is in use. Please ensure that the file is not open by another application.',
        '504_title': 'Cannot watch filesystem',
        '504_description': 'Cannot watch filesystem. Please run \'sudo sysctl -w fs.inotify.max_user_watches=100000\' and restart MEO Cloud to fix the problem.',
    },
    'pt': {
        '200_title': 'Ficheiro Adicionado',
        '200_description': 'O ficheiro "{0}" foi adicionado à pasta MEO Cloud',
        '201_title': 'Ficheiro Removido',
        '201_description': 'O ficheiro "{0}" foi removido da pasta MEO Cloud',
        '202_title': 'Ficheiro Atualizado',
        '202_description': 'O ficheiro "{0}" foi atualizado na pasta MEO Cloud',
        '203_title': 'Ficheiros Adicionados',
        '203_description': '{0} ficheiros foram adicionados à pasta MEO Cloud',
        '204_title': 'Ficheiros Removidos',
        '204_description': '{0} ficheiros foram removidos da pasta MEO Cloud',
        '205_title': 'Ficheiros Atualizados',
        '205_description': '{0} ficheiros foram atualizados na pasta MEO Cloud',
        '206_title': 'Ficheiros Sincronizados',
        '206_description': '{0} ficheiros foram sincronizados na pasta MEO Cloud',
        '207_title': 'A ligar à MEO Cloud...',
        '207_description': 'Por favor verifique a sua ligação à Internet e as definições do proxy.',

        '250_title': 'Pasta Partilhada Criada',
        '250_description': 'A pasta partilhada "{0}" foi criada na pasta MEO Cloud',
        '251_title': 'Pasta Parilhada Apagada',
        '251_description': 'A pasta partilhada "{0}" foi apagada da pasta MEO Cloud',
        '252_title': 'Pasta Não Partilhada',
        '252_description': 'A pasta "{0}" deixou de estar partilhada',

        '500_title': 'Excedeu a quota',
        '500_description': 'Excedeu a sua quota MEO Cloud. Por favor liberte algum espaço para continuar a fazer upload.',
        '501_title': 'Não foi possível sincronizar "{0}"',
        '501_description': 'Não foi possível sincronizar "{0}". Por favor verifique que tem permissões suficientes e o ficheiro não está a ser usado.',
        '502_title': 'Espaço em disco insuficiente',
        '502_description': 'Não foi possível actualizar "{0}". Por favor verfique o espaço livre do seu disco.',
        '503_title': 'O ficheiro "{0}" está em uso',
        '503_description': 'O ficheiro "{0}" está em uso. Por favor verifique se o ficheiro está aberto em alguma aplicação.',
        '504_title': 'Não é possível monitorizar ficheiros',
        '504_description': 'Não é possível monitorizar ficheiros. Para resolver o problema, por favor execute o comando \'sudo sysctl -w fs.inotify.max_user_watches=100000\' e reinice a aplicação.',
    },
}
