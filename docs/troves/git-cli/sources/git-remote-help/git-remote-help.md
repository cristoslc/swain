---
source-id: "git-remote-help"
title: "git remote --help"
type: cli-subcommand-help
tool-name: "git"
command: "remote"
depth: 1
fetched: 2026-04-07T20:22:53Z
hash: "a568342c5b340bb4232eb9a5ee7aa49f37df811229f0041c67902b88358bd810"
---

# git remote --help

GIT-REMOTE(1)                     Git Manual                     GIT-REMOTE(1)

NNAAMMEE
       git-remote - Manage set of tracked repositories

SSYYNNOOPPSSIISS
       ggiitt rreemmoottee [--vv | ----vveerrbboossee]
       ggiitt rreemmoottee aadddd [--tt _<_b_r_a_n_c_h_>] [--mm _<_m_a_s_t_e_r_>] [--ff] [----[nnoo--]ttaaggss] [----mmiirrrroorr==(ffeettcchh|ppuusshh)] _<_n_a_m_e_> _<_U_R_L_>
       ggiitt rreemmoottee rreennaammee [----[nnoo--]pprrooggrreessss] _<_o_l_d_> _<_n_e_w_>
       ggiitt rreemmoottee rreemmoovvee _<_n_a_m_e_>
       ggiitt rreemmoottee sseett--hheeaadd _<_n_a_m_e_> (--aa | ----aauuttoo | --dd | ----ddeelleettee | _<_b_r_a_n_c_h_>)
       ggiitt rreemmoottee sseett--bbrraanncchheess [----aadddd] _<_n_a_m_e_> _<_b_r_a_n_c_h_>...
       ggiitt rreemmoottee ggeett--uurrll [----ppuusshh] [----aallll] _<_n_a_m_e_>
       ggiitt rreemmoottee sseett--uurrll [----ppuusshh] _<_n_a_m_e_> _<_n_e_w_u_r_l_> [_<_o_l_d_u_r_l_>]
       ggiitt rreemmoottee sseett--uurrll ----aadddd [----ppuusshh] _<_n_a_m_e_> _<_n_e_w_u_r_l_>
       ggiitt rreemmoottee sseett--uurrll ----ddeelleettee [----ppuusshh] _<_n_a_m_e_> _<_U_R_L_>
       ggiitt rreemmoottee [--vv | ----vveerrbboossee] sshhooww [--nn] _<_n_a_m_e_>...
       ggiitt rreemmoottee pprruunnee [--nn | ----ddrryy--rruunn] _<_n_a_m_e_>...
       ggiitt rreemmoottee [--vv | ----vveerrbboossee] uuppddaattee [--pp | ----pprruunnee] [(_<_g_r_o_u_p_> | _<_r_e_m_o_t_e_>)...]

DDEESSCCRRIIPPTTIIOONN
       Manage the set of repositories ("remotes") whose branches you track.

OOPPTTIIOONNSS
       --vv, ----vveerrbboossee
           Be a little more verbose and show remote url after name. For
           promisor remotes, also show which filters (bblloobb::nnoonnee etc.) are
           configured. NOTE: This must be placed between rreemmoottee and
           subcommand.

CCOOMMMMAANNDDSS
       With no arguments, show a list of existing remotes. Several subcommands
       are available to perform operations on the remotes.

       aadddd
           Add a remote named _<_n_a_m_e_> for the repository at _<_U_R_L_>. The command
           ggiitt ffeettcchh _<_n_a_m_e_> can then be used to create and update
           remote-tracking branches _<_n_a_m_e_>//_<_b_r_a_n_c_h_>.

           With --ff option, ggiitt ffeettcchh _<_n_a_m_e_> is run immediately after the
           remote information is set up.

           With ----ttaaggss option, ggiitt ffeettcchh _<_n_a_m_e_> imports every tag from the
           remote repository.

           With ----nnoo--ttaaggss option, ggiitt ffeettcchh _<_n_a_m_e_> does not import tags from
           the remote repository.

           By default, only tags on fetched branches are imported (see ggiitt--
           ffeettcchh(1)).

           With --tt _<_b_r_a_n_c_h_> option, instead of the default glob refspec for
           the remote to track all branches under the rreeffss//rreemmootteess//_<_n_a_m_e_>//
           namespace, a refspec to track only _<_b_r_a_n_c_h_> is created. You can
           give more than one --tt _<_b_r_a_n_c_h_> to track multiple branches without
           grabbing all branches.

           With --mm _<_m_a_s_t_e_r_> option, a symbolic-ref rreeffss//rreemmootteess//_<_n_a_m_e_>//HHEEAADD is
           set up to point at remote’s _<_m_a_s_t_e_r_> branch. See also the set-head
           command.

           When a fetch mirror is created with ----mmiirrrroorr==ffeettcchh, the refs will
           not be stored in the rreeffss//rreemmootteess// namespace, but rather everything
           in rreeffss// on the remote will be directly mirrored into rreeffss// in the
           local repository. This option only makes sense in bare
           repositories, because a fetch would overwrite any local commits.

           When a push mirror is created with ----mmiirrrroorr==ppuusshh, then ggiitt ppuusshh
           will always behave as if ----mmiirrrroorr was passed.

       rreennaammee
           Rename the remote named _<_o_l_d_> to _<_n_e_w_>. All remote-tracking
           branches and configuration settings for the remote are updated.

           In case _<_o_l_d_> and _<_n_e_w_> are the same, and _<_o_l_d_> is a file under
           $$GGIITT__DDIIRR//rreemmootteess or $$GGIITT__DDIIRR//bbrraanncchheess, the remote is converted to
           the configuration file format.

       rreemmoovvee, rrmm
           Remove the remote named _<_n_a_m_e_>. All remote-tracking branches and
           configuration settings for the remote are removed.

       sseett--hheeaadd
           Set or delete the default branch (i.e. the target of the
           symbolic-ref rreeffss//rreemmootteess//_<_n_a_m_e_>//HHEEAADD) for the named remote. Having
           a default branch for a remote is not required, but allows the name
           of the remote to be specified in lieu of a specific branch. For
           example, if the default branch for oorriiggiinn is set to mmaasstteerr, then
           oorriiggiinn may be specified wherever you would normally specify
           oorriiggiinn//mmaasstteerr.

           With --dd or ----ddeelleettee, the symbolic ref rreeffss//rreemmootteess//_<_n_a_m_e_>//HHEEAADD is
           deleted.

           With --aa or ----aauuttoo, the remote is queried to determine its HHEEAADD,
           then the symbolic-ref rreeffss//rreemmootteess//_<_n_a_m_e_>//HHEEAADD is set to the same
           branch. e.g., if the remote HHEEAADD is pointed at nneexxtt, ggiitt rreemmoottee
           sseett--hheeaadd oorriiggiinn --aa will set the symbolic-ref
           rreeffss//rreemmootteess//oorriiggiinn//HHEEAADD to rreeffss//rreemmootteess//oorriiggiinn//nneexxtt. This will
           only work if rreeffss//rreemmootteess//oorriiggiinn//nneexxtt already exists; if not it
           must be fetched first.

           Use _<_b_r_a_n_c_h_> to set the symbolic-ref rreeffss//rreemmootteess//_<_n_a_m_e_>//HHEEAADD
           explicitly. e.g., ggiitt rreemmoottee sseett--hheeaadd oorriiggiinn mmaasstteerr will set the
           symbolic-ref rreeffss//rreemmootteess//oorriiggiinn//HHEEAADD to
           rreeffss//rreemmootteess//oorriiggiinn//mmaasstteerr. This will only work if
           rreeffss//rreemmootteess//oorriiggiinn//mmaasstteerr already exists; if not it must be
           fetched first.

       sseett--bbrraanncchheess
           Change the list of branches tracked by the named remote. This can
           be used to track a subset of the available remote branches after
           the initial setup for a remote.

           The named branches will be interpreted as if specified with the --tt
           option on the ggiitt rreemmoottee aadddd command line.

           With ----aadddd, instead of replacing the list of currently tracked
           branches, adds to that list.

       ggeett--uurrll
           Retrieves the URLs for a remote. Configurations for iinnsstteeaaddOOff and
           ppuusshhIInnsstteeaaddOOff are expanded here. By default, only the first URL is
           listed.

           With ----ppuusshh, push URLs are queried rather than fetch URLs.

           With ----aallll, all URLs for the remote will be listed.

       sseett--uurrll
           Change URLs for the remote. Sets first URL for remote _<_n_a_m_e_> that
           matches regex _<_o_l_d_u_r_l_> (first URL if no _<_o_l_d_u_r_l_> is given) to
           _<_n_e_w_u_r_l_>. If _<_o_l_d_u_r_l_> doesn’t match any URL, an error occurs and
           nothing is changed.

           With ----ppuusshh, push URLs are manipulated instead of fetch URLs.

           With ----aadddd, instead of changing existing URLs, new URL is added.

           With ----ddeelleettee, instead of changing existing URLs, all URLs matching
           regex _<_U_R_L_> are deleted for remote _<_n_a_m_e_>. Trying to delete all
           non-push URLs is an error.

           Note that the push URL and the fetch URL, even though they can be
           set differently, must still refer to the same place. What you
           pushed to the push URL should be what you would see if you
           immediately fetched from the fetch URL. If you are trying to fetch
           from one place (e.g. your upstream) and push to another (e.g. your
           publishing repository), use two separate remotes.

       sshhooww
           Give some information about the remote _<_n_a_m_e_>.

           With --nn option, the remote heads are not queried first with ggiitt
           llss--rreemmoottee _<_n_a_m_e_>; cached information is used instead.

       pprruunnee
           Delete stale references associated with _<_n_a_m_e_>. By default, stale
           remote-tracking branches under _<_n_a_m_e_> are deleted, but depending on
           global configuration and the configuration of the remote we might
           even prune local tags that haven’t been pushed there. Equivalent to
           ggiitt ffeettcchh ----pprruunnee _<_n_a_m_e_>, except that no new references will be
           fetched.

           See the PRUNING section of ggiitt--ffeettcchh(1) for what it’ll prune
           depending on various configuration.

           With ----ddrryy--rruunn option, report what branches would be pruned, but do
           not actually prune them.

       uuppddaattee
           Fetch updates for remotes or remote groups in the repository as
           defined by rreemmootteess.._<_g_r_o_u_p_>. If neither group nor remote is
           specified on the command line, the configuration parameter
           rreemmootteess..ddeeffaauulltt will be used; if rreemmootteess..ddeeffaauulltt is not defined,
           all remotes which do not have the configuration parameter
           rreemmoottee.._<_n_a_m_e_>..sskkiippDDeeffaauullttUUppddaattee set to ttrruuee will be updated. (See
           ggiitt--ccoonnffiigg(1)).

           With ----pprruunnee option, run pruning against all the remotes that are
           updated.

DDIISSCCUUSSSSIIOONN
       The remote configuration is achieved using the rreemmoottee..oorriiggiinn..uurrll and
       rreemmoottee..oorriiggiinn..ffeettcchh configuration variables. (See ggiitt--ccoonnffiigg(1)).

EEXXIITT SSTTAATTUUSS
       On success, the exit status is 00.

       When subcommands such as aadddd, rreennaammee, and rreemmoovvee can’t find the remote
       in question, the exit status is 22. When the remote already exists, the
       exit status is 33.

       On any other error, the exit status may be any other non-zero value.

EEXXAAMMPPLLEESS
       •   Add a new remote, fetch, and check out a branch from it

               $ git remote
               origin
               $ git branch -r
                 origin/HEAD -> origin/master
                 origin/master
               $ git remote add staging git://git.kernel.org/.../gregkh/staging.git
               $ git remote
               origin
               staging
               $ git fetch staging
               ...
               From git://git.kernel.org/pub/scm/linux/kernel/git/gregkh/staging
                * [new branch]      master     -> staging/master
                * [new branch]      staging-linus -> staging/staging-linus
                * [new branch]      staging-next -> staging/staging-next
               $ git branch -r
                 origin/HEAD -> origin/master
                 origin/master
                 staging/master
                 staging/staging-linus
                 staging/staging-next
               $ git switch -c staging staging/master
               ...

       •   Imitate ggiitt cclloonnee but track only selected branches

               $ mkdir project.git
               $ cd project.git
               $ git init
               $ git remote add -f -t master -m master origin git://example.com/git.git/
               $ git merge origin

SSEEEE AALLSSOO
       ggiitt--ffeettcchh(1) ggiitt--bbrraanncchh(1) ggiitt--ccoonnffiigg(1)

GGIITT
       Part of the ggiitt(1) suite

Git 2.53.0                        2026-02-01                     GIT-REMOTE(1)
